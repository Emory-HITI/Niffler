set terminal pdf

# This is to set the colors of the plot

set datafile separator ","

set palette rgb 34,35,36

set boxwidth 0.5
set style fill solid

set xtics font "Verdana,16" 
set ytics font "Verdana,16" 
set cbtics font "Verdana,16"
set xlabel font "Verdana,16" 
set ylabel font "Verdana,16" 
set cblabel font "Verdana,16"
set key font "Verdana,16" 
set cbrange [1:22]
set cbtics add (1, 22)
set cblabel "No. of Encounters" offset 2,0,0
set grid

do for [index in "26356 35386 31130 69618 25992 41546 41563 145596 141301 45988 145384 141638 000000000000GEMS 000000404251EOMR 000000678474JCMR 00000678474JCMR2 42458 00ALLIANCESIG479 25285 25240 142105 000000404256AMR1 145624 141780 141676"] {
set yrange [0:100]
set xrange [0:29]

set xlabel "Day"
set ylabel "Utilization (%)"

set output index.'.pdf'
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq index  ? $4 : 1/0): 6: xticlabel((stringcolumn(3) eq index)?$4 : 1/0) with boxes lt palette fs solid border 1.0 notitle

unset yrange
set xlabel "Day"
set ylabel "No. of Patients"

set output 'p'.index.'.pdf'
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq index  ? $5 : 1/0): xticlabel((stringcolumn(3) eq index)?$5 : 1/0) with boxes notitle


set xlabel "Day"
set ylabel "No. of Encounters"

set output 'e'.index.'.pdf'
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq index  ? $6 : 1/0): xticlabel((stringcolumn(3) eq index)?$6 : 1/0) with boxes notitle

set xlabel "Day"
set ylabel "No. of Studies"

set output 'st'.index.'.pdf'
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq index  ? $7 : 1/0): xticlabel((stringcolumn(3) eq index)?$7 : 1/0) with boxes notitle

set xlabel "Day"
set ylabel "No. of Series"

set output 'se'.index.'.pdf'
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq index  ? $9 : 1/0): xticlabel((stringcolumn(3) eq index)?$9 : 1/0) with boxes notitle

}

