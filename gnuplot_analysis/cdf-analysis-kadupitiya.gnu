reset
# set fontpath \
# "/usr/share/texmf/fonts/type1/public/cm-super/" \
# "/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/"
set terminal postscript eps enhanced color lw 1.5 dl 3.0 \
    font 'Helvetica' 
# # fontfile 'cmmi10.pfb' \
# # fontfile 'cmr10.pfb' \
# # fontfile 'cmmib10.pfb' \
# # fontfile 'cmti10.pfb'
  
set border linewidth 1
set style line 1 linecolor rgb 'red' linetype 1 linewidth 1 pointtype 6 pointsize 1
set style line 2 linecolor rgb 'green' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 3 linecolor rgb 'blue' linetype 1 linewidth 1 pointtype 6 pointsize 1
set style line 4 linecolor rgb 'orange' linetype 1 linewidth 1 pointtype 6 pointsize 1
set style line 5 linecolor rgb 'black' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 6 linecolor rgb 'magenta' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 7 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 8 linecolor rgb 'purple' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 9 linecolor rgb 'olive' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 10 linecolor rgb 'pink' linetype 1 linewidth 1 pointtype 6 pointsize 1
set style line 12 linecolor rgb 'green' linetype 2 linewidth 1 pointtype 6 pointsize 1
set style line 13 linecolor rgb 'blue' linetype 2 linewidth 1 pointtype 6 pointsize 1
set style line 14 linecolor rgb 'orange' linetype 3 linewidth 1 pointtype 6 pointsize 1
set style line 15 linecolor rgb 'cyan' linetype 3 linewidth 1 pointtype 6 pointsize 1
set style line 16 linecolor rgb 'magenta' linetype 2 linewidth 1 pointtype 6 pointsize 1

#for figures in scispot
set style line 10 linecolor rgb 'red' linetype 1 linewidth 1 pointtype 6 pointsize 1.5 #for data
set style line 5 linecolor rgb 'black' linetype 1 linewidth 2 pointtype 6  pointsize 1
set style line 1 linecolor rgb 'brown' linetype 2 linewidth 2 pointtype 6 pointsize 1
set style line 3 linecolor rgb 'blue' linetype 4 linewidth 2 pointtype 6 pointsize 1

set style line 11 linecolor rgb 'blue' linetype 1 linewidth 1 pointtype 4 pointsize 1.5 #for data
set style line 12 linecolor rgb 'cyan' linetype 1 linewidth 1 pointtype 12 pointsize 1.5 #for data
set style line 13 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 8 pointsize 1.5 #for data
set style line 14 linecolor rgb 'black' linetype 1 linewidth 1 pointtype 10 pointsize 1.5 #for data

set style line 15 linecolor rgb 'red' linetype 1 linewidth 2 pointtype 6  pointsize 1
set style line 16 linecolor rgb 'blue' linetype 2 linewidth 2 pointtype 6  pointsize 1
set style line 17 linecolor rgb 'cyan' linetype 4 linewidth 2 pointtype 6  pointsize 1
set style line 18 linecolor rgb 'brown' linetype 5 linewidth 2 pointtype 6  pointsize 1
set style line 19 linecolor rgb 'black' linetype 3 linewidth 2 pointtype 6  pointsize 1

set style line 2 linecolor rgb 'green' linetype 3 linewidth 1 pointtype 6  pointsize 1
set style line 4 linecolor rgb 'orange' linetype 5 linewidth 1 pointtype 6 pointsize 1
set style line 6 linecolor rgb 'magenta' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 7 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 8 linecolor rgb 'purple' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 9 linecolor rgb 'olive' linetype 1 linewidth 1 pointtype 6  pointsize 1

set tics nomirror

set origin 0,0
set size 0.8,0.6
set border linewidth 1

set autoscale x
set autoscale y
set output 'figures/region-breakdown.eps'
set key vertical width 2 maxrows 10

set key top left
#set key at 9,0.8
#set key samplen 2
set key spacing 1
set key font 'Helvetica, 22'
set xtics font "Helvetica, 22"
set ytics font "Helvetica, 22"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,24'
set ylabel 'CDF' font 'Helvetica,24'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.1]
#plot  set8f(x) with l ls 15 title 'Idle',\
#set16f(x) with l ls 15 dashtype 3 title 'Non-idle', \
#set2f(x) with l ls 19 dashtype 3 title 'Night', \
#set4f(x) with l ls 19 title  'Day', \

plot 'blended_exp_models/us-central1-c.txt' u 1:2 every 1 with l ls 15 title 'us-central1-c',\
'blended_exp_models/us-central1-c.txt' u 1:2 every 1 with l ls 16 title 'us-central1-c',\
'blended_exp_models/us-central1-c.txt' u 1:2 every 1 with l ls 17 title 'us-central1-c',\
'blended_exp_models/us-central1-c.txt' u 1:2 every 1 with l ls 18 title 'us-central1-c'
 
exit

