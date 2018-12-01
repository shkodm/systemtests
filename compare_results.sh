#!/bin/bash

# Rough estimate of difference in numerical results for SU2, Caculix and OpenFOAM files
# might need future parsing fixes for future adapters (awk will complain when this happen)
#
# Input: folder where results should be compared and maximum relative difference between
# numerical values

folder1="$1"
folder2="$2"
diff_limit="$3"

diff_result=$( diff -rq $folder1 $folder2 )

# split result into two, depending whether files are unique in one folder
# or just differ
diff_files=$( echo "$diff_result" | sed '/Only/d' )
only_files=$( echo "$diff_result" | sed '/differ/d')


if [ -n "$diff_files" ]; then
  mapfile -t array_files < <( echo "$diff_files"  | sed 's/Files\|and\|differ//g' )
  arr_len="${#array_files[@]}"

  for (( i = 0; i<${arr_len}; i = i + 1));
  do
    file1=$( echo "${array_files[i]}" | awk '{print $1}' )
    file2=$( echo "${array_files[i]}" | awk '{print $2}' )
    rawdiff=$( diff -y --speed-large-files --suppress-common-lines "$file1" "$file2" )
    # rought guess of results values
    # filter resuls, ignore 'lines with words (probably not the results), careful about exponent
    # removes |<>() characters, that will mess up with awk
    # Carefull about "e", since it is used as exponent in FP values
    filtered_diff=$( echo "$rawdiff" | sed 's/(\|)\||\|>\|<//g; /[a-df-zA-Z]\|Version/d' )

    # Paiwise compares files fields, that are produces from diffs and computes relative difference
    if [ -n "$filtered_diff" ]; then
      rel_difference=$( echo "$filtered_diff" | awk -v diff_limit="$diff_limit" 'function abs(v) {return v < 0 ? -v : v} { radius=NF/2; for(i = 1; i <= radius;
      i++) { if ($i != 0) { sum += abs((($(i + radius)-$i)/$i )) } } } END { diff=sum/( NR*radius ); if (diff > diff_limit)  { print diff }}')
    fi

    if [ -n "$rel_difference" ]; then
      echo "Relative difference between $file1 and $file2 is $rel_difference percent"
    #  diff -yr --suppress-common-lines "$1" "$2"
    fi
  done
fi

echo "$only_files"
