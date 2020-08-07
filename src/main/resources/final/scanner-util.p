# a scatter plot that shows the correlation between
# wind production and total consumption

# This is to set the colors of the plot
set term png background "white" 
set datafile separator ","
#set key below

set boxwidth 0.5
set style fill solid

set xtics font "Verdana,16" 
set ytics font "Verdana,16" 


set xlabel font "Verdana,16" 
set ylabel font "Verdana,16" 
set key font "Verdana,16" 

set yrange [0:110.5]



set xlabel "Day"
set ylabel "Utilization (%)"


set output "26356.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "26356"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "26356")?$4 : 1/0) with boxes notitle

set output "35386.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "35386"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "35386")?$4 : 1/0) with boxes notitle

set output "31130.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "31130"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "31130")?$4 : 1/0) with boxes notitle

set output "69618.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "69618"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "69618")?$4 : 1/0) with boxes notitle

set output "25992.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25992"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "25992")?$4 : 1/0) with boxes notitle

set output "41546.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41546"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "41546")?$4 : 1/0) with boxes notitle

set output "41563.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41563"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "41563")?$4 : 1/0) with boxes notitle

set output "145596.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145596"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "145596")?$4 : 1/0) with boxes notitle

set output "141301.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141301"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "141301")?$4 : 1/0) with boxes notitle

set output "45988.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "45988"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "45988")?$4 : 1/0) with boxes notitle

set output "145384.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145384"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "145384")?$4 : 1/0) with boxes notitle

set output "141638.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141638"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "141638")?$4 : 1/0) with boxes notitle

set output "000000000000GEMS.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000000000GEMS"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "000000000000GEMS")?$4 : 1/0) with boxes notitle

set output "000000404251EOMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404251EOMR"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "000000404251EOMR")?$4 : 1/0) with boxes notitle

set output "000000678474JCMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000678474JCMR"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "000000678474JCMR")?$4 : 1/0) with boxes notitle

set output "00000678474JCMR2.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00000678474JCMR2"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "00000678474JCMR2")?$4 : 1/0) with boxes notitle

set output "42458.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "42458"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "42458")?$4 : 1/0) with boxes notitle

set output "00ALLIANCESIG479.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00ALLIANCESIG479"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "00ALLIANCESIG479")?$4 : 1/0) with boxes notitle

set output "25285.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25285"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "25285")?$4 : 1/0) with boxes notitle

set output "25240.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25240"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "25240")?$4 : 1/0) with boxes notitle

set output "142105.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "142105"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "142105")?$4 : 1/0) with boxes notitle

set output "000000404256AMR1.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404256AMR1"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "000000404256AMR1")?$4 : 1/0) with boxes notitle

set output "145624.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145624"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "145624")?$4 : 1/0) with boxes notitle

set output "141780.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141780"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "141780")?$4 : 1/0) with boxes notitle

set output "141676.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141676"  ? $4 : 1/0): xticlabel((stringcolumn(3) eq "141676")?$4 : 1/0) with boxes notitle




unset yrange







set xlabel "Day"
set ylabel "No. of Patients"


set output "p26356.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "26356"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "26356")?$5 : 1/0) with boxes notitle

set output "p35386.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "35386"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "35386")?$5 : 1/0) with boxes notitle

set output "p31130.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "31130"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "31130")?$5 : 1/0) with boxes notitle

set output "p69618.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "69618"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "69618")?$5 : 1/0) with boxes notitle

set output "p25992.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25992"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "25992")?$5 : 1/0) with boxes notitle

set output "p41546.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41546"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "41546")?$5 : 1/0) with boxes notitle

set output "p41563.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41563"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "41563")?$5 : 1/0) with boxes notitle

set output "p145596.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145596"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "145596")?$5 : 1/0) with boxes notitle

set output "p141301.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141301"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "141301")?$5 : 1/0) with boxes notitle

set output "p45988.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "45988"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "45988")?$5 : 1/0) with boxes notitle

set output "p145384.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145384"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "145384")?$5 : 1/0) with boxes notitle

set output "p141638.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141638"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "141638")?$5 : 1/0) with boxes notitle

set output "p000000000000GEMS.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000000000GEMS"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "000000000000GEMS")?$5 : 1/0) with boxes notitle

set output "p000000404251EOMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404251EOMR"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "000000404251EOMR")?$5 : 1/0) with boxes notitle

set output "p000000678474JCMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000678474JCMR"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "000000678474JCMR")?$5 : 1/0) with boxes notitle

set output "p00000678474JCMR2.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00000678474JCMR2"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "00000678474JCMR2")?$5 : 1/0) with boxes notitle

set output "p42458.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "42458"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "42458")?$5 : 1/0) with boxes notitle

set output "p00ALLIANCESIG479.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00ALLIANCESIG479"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "00ALLIANCESIG479")?$5 : 1/0) with boxes notitle

set output "p25285.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25285"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "25285")?$5 : 1/0) with boxes notitle

set output "p25240.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25240"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "25240")?$5 : 1/0) with boxes notitle

set output "p142105.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "142105"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "142105")?$5 : 1/0) with boxes notitle

set output "p000000404256AMR1.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404256AMR1"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "000000404256AMR1")?$5 : 1/0) with boxes notitle

set output "p145624.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145624"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "145624")?$5 : 1/0) with boxes notitle

set output "p141780.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141780"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "141780")?$5 : 1/0) with boxes notitle

set output "p141676.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141676"  ? $5 : 1/0): xticlabel((stringcolumn(3) eq "141676")?$5 : 1/0) with boxes notitle














set xlabel "Day"
set ylabel "No. of Exams"


set output "e26356.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "26356"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "26356")?$6 : 1/0) with boxes notitle

set output "e35386.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "35386"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "35386")?$6 : 1/0) with boxes notitle

set output "e31130.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "31130"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "31130")?$6 : 1/0) with boxes notitle

set output "e69618.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "69618"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "69618")?$6 : 1/0) with boxes notitle

set output "e25992.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25992"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "25992")?$6 : 1/0) with boxes notitle

set output "e41546.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41546"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "41546")?$6 : 1/0) with boxes notitle

set output "e41563.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "41563"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "41563")?$6 : 1/0) with boxes notitle

set output "e145596.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145596"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "145596")?$6 : 1/0) with boxes notitle

set output "e141301.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141301"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "141301")?$6 : 1/0) with boxes notitle

set output "e45988.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "45988"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "45988")?$6 : 1/0) with boxes notitle

set output "e145384.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145384"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "145384")?$6 : 1/0) with boxes notitle

set output "e141638.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141638"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "141638")?$6 : 1/0) with boxes notitle

set output "e000000000000GEMS.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000000000GEMS"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "000000000000GEMS")?$6 : 1/0) with boxes notitle

set output "e000000404251EOMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404251EOMR"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "000000404251EOMR")?$6 : 1/0) with boxes notitle

set output "e000000678474JCMR.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000678474JCMR"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "000000678474JCMR")?$6 : 1/0) with boxes notitle

set output "e00000678474JCMR2.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00000678474JCMR2"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "00000678474JCMR2")?$6 : 1/0) with boxes notitle

set output "e42458.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "42458"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "42458")?$6 : 1/0) with boxes notitle

set output "e00ALLIANCESIG479.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "00ALLIANCESIG479"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "00ALLIANCESIG479")?$6 : 1/0) with boxes notitle

set output "e25285.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25285"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "25285")?$6 : 1/0) with boxes notitle

set output "e25240.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "25240"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "25240")?$6 : 1/0) with boxes notitle

set output "e142105.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "142105"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "142105")?$6 : 1/0) with boxes notitle

set output "e000000404256AMR1.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "000000404256AMR1"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "000000404256AMR1")?$6 : 1/0) with boxes notitle

set output "e145624.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "145624"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "145624")?$6 : 1/0) with boxes notitle

set output "e141780.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141780"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "141780")?$6 : 1/0) with boxes notitle

set output "e141676.png"
plot "scanner-util.csv" using 1:(  stringcolumn(3) eq "141676"  ? $6 : 1/0): xticlabel((stringcolumn(3) eq "141676")?$6 : 1/0) with boxes notitle

