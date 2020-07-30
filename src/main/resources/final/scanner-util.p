# a scatter plot that shows the correlation between
# wind production and total consumption

# This is to set the colors of the plot
set term png background "white" 
set datafile separator ","
#set key below
set style line 1 lc rgb "blue" lw 2 pt 2
set xtics font "Verdana,16" 
set ytics font "Verdana,16" 


set xlabel font "Verdana,16" 
set ylabel font "Verdana,16" 
set key font "Verdana,16" 

set xrange [-0.5:31.5]
set yrange [0:110.5]



set xlabel "Date"
set ylabel "Utilization (%)"


set output "26356.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "26356"  ? $4 : 1/0) with linespoints ls 1 title "26356"

set output "38386.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "38386"  ? $4 : 1/0) with linespoints ls 1 title "38386"

set output "31130.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "31130"  ? $4 : 1/0) with linespoints ls 1 title "31130"

set output "69618.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "69618"  ? $4 : 1/0) with linespoints ls 1 title "69618"

set output "25992.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "25992"  ? $4 : 1/0) with linespoints ls 1 title "25992"

set output "41546.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "41546"  ? $4 : 1/0) with linespoints ls 1 title "41546"

set output "41563.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "41563"  ? $4 : 1/0) with linespoints ls 1 title "41563"

set output "145596.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "145596"  ? $4 : 1/0) with linespoints ls 1 title "145596"

set output "141301.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "141301"  ? $4 : 1/0) with linespoints ls 1 title "141301"

set output "45988.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "45988"  ? $4 : 1/0) with linespoints ls 1 title "45988"

set output "145384.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "145384"  ? $4 : 1/0) with linespoints ls 1 title "145384"

set output "141638.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "141638"  ? $4 : 1/0) with linespoints ls 1 title "141638"

set output "000000000000GEMS.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "000000000000GEMS"  ? $4 : 1/0) with linespoints ls 1 title "000000000000GEMS"

set output "000000404251EOMR.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "000000404251EOMR"  ? $4 : 1/0) with linespoints ls 1 title "000000404251EOMR"

set output "000000678474JCMR.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "000000678474JCMR"  ? $4 : 1/0) with linespoints ls 1 title "000000678474JCMR"

set output "00000678474JCMR2.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "00000678474JCMR2"  ? $4 : 1/0) with linespoints ls 1 title "00000678474JCMR2"

set output "42458.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "42458"  ? $4 : 1/0) with linespoints ls 1 title "42458"

set output "00ALLIANCESIG479.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "00ALLIANCESIG479"  ? $4 : 1/0) with linespoints ls 1 title "00ALLIANCESIG479"

set output "25285.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "25285"  ? $4 : 1/0) with linespoints ls 1 title "25285"

set output "25240.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "25240"  ? $4 : 1/0) with linespoints ls 1 title "25240"

set output "142105.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "142105"  ? $4 : 1/0) with linespoints ls 1 title "142105"

set output "000000404256AMR1.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "000000404256AMR1"  ? $4 : 1/0) with linespoints ls 1 title "000000404256AMR1"

set output "145624.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "145624"  ? $4 : 1/0) with linespoints ls 1 title "145624"

set output "141780.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "141780"  ? $4 : 1/0) with linespoints ls 1 title "141780"

set output "141676.png"
plot "scanner-util.csv" using 1:(  (sprintf('%s', stringcolumn(3))) eq "141676"  ? $4 : 1/0) with linespoints ls 1 title "141676"

