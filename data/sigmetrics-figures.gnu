reset
set fontpath \
"/usr/share/texmf/fonts/type1/public/cm-super/" \
"/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/"
set terminal postscript eps enhanced color lw 1.0 dl 3.0 \
font 'Helvetica' \
#fontfile 'cmmi10.pfb' \
#fontfile 'cmr10.pfb' \
#fontfile 'cmmib10.pfb' \
#fontfile 'cmti10.pfb'
  
set border linewidth 1

#for figures in sigmetrics

set style line 11 linecolor rgb 'blue' linetype 1 linewidth 1 pointtype 4 pointsize 1.5 #for data
set style line 12 linecolor rgb 'cyan' linetype 1 linewidth 1 pointtype 12 pointsize 1.5 #for data
set style line 13 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 8 pointsize 1.5 #for data
set style line 14 linecolor rgb 'black' linetype 1 linewidth 1 pointtype 10 pointsize 1.5 #for data

set style line 15 linecolor rgb 'red' linetype 1 linewidth 2 pointtype 6  pointsize 1
set style line 16 linecolor rgb 'blue' linetype 2 linewidth 2 pointtype 6  pointsize 1
set style line 17 linecolor rgb 'cyan' linetype 4 linewidth 2 pointtype 6  pointsize 1
set style line 18 linecolor rgb 'brown' linetype 5 linewidth 2 pointtype 6  pointsize 1
set style line 19 linecolor rgb 'black' linetype 3 linewidth 2 pointtype 6  pointsize 1

set style line 20 linecolor rgb 'black' linetype 1 linewidth 2 pointtype 6  pointsize 1
set style line 21 linecolor rgb 'red' linetype 3 linewidth 2 pointtype 6  pointsize 1

set style line 1 linecolor rgb 'brown' linetype 2 linewidth 2 pointtype 6 pointsize 1
set style line 2 linecolor rgb 'green' linetype 3 linewidth 1 pointtype 6  pointsize 1
set style line 3 linecolor rgb 'blue' linetype 4 linewidth 2 pointtype 6 pointsize 1
set style line 4 linecolor rgb 'olive' linetype 5  linewidth 1 pointtype 6 pointsize 1
set style line 5 linecolor rgb 'black' linetype 3 linewidth 2 pointtype 6  pointsize 1
set style line 6 linecolor rgb 'magenta' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 7 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 8 linecolor rgb 'purple' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 9 linecolor rgb 'olive' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 10 linecolor rgb 'red' linetype 1 linewidth 1 pointtype 6 pointsize 1.5 #for data

set tics nomirror
set autoscale x
set autoscale y
set output 'gnuplot-figures/sigmetrics-fig-cdf-prob-inset-time.eps'
set multiplot
set origin 0,0
set size 1,1
set key vertical width 2 maxrows 10
set key bottom right
set key spacing 1
set key font 'Helvetica, 24'
set xtics font "Helvetica, 24"
set ytics font "Helvetica, 24"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,24'
set ylabel 'CDF' font 'Helvetica,24'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.02]
plot \
'runtime-data-by-group/All_data.txt' u 1:2 every 1 t 'Empirical Data' with p ls 10, \
'runtime-data-by-group/blended_exp_model/All_data.txt' u 1:2 every 3 t 'Our Model' w l ls 5 lw 3, \
'runtime-data-by-group/plain_exp_model/All_data.txt' u 1:2 every 3 t 'Classical Exponential' w l ls 1, \
'runtime-data-by-group/weibull/All_data.txt' u 1:2 every 3 t 'Classic Weibull' w l ls 3, \
'runtime-data-by-group/gm_model/All_data.txt' u 1:2 every 2 t 'Gompertz-Makeham' w l ls 4 lw 3 dashtype 3
set origin 0.105,0.6
set size 0.42, 0.38
set border linewidth 0.5
set autoscale x
set autoscale y
unset key
set xtics font "Helvetica, 18"
set ytics font "Helvetica, 18"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
unset xlabel
set ylabel 'Probability' font 'Helvetica,18'
set xlabel offset 0,0
set ylabel offset 1,0
set xrange [0:25]
set yrange [0:1]
plot \
'runtime-data-by-group/blended_exp_model/All_data_diff.txt' u 1:2 every 3 t 'Our Model' w l ls 5, \
'runtime-data-by-group/plain_exp_model/All_data_diff.txt' u 1:2 every 3 t 'Classical Exponential' w l ls 1, \
'runtime-data-by-group/weibull/All_data_diff.txt' u 1:2 every 3 t 'Classic Weibull' w l ls 3, \
'runtime-data-by-group/gm_model/All_data_diff.txt' u 1:2 every 4 t 'Gompertz-Makeham' w l ls 4 

unset multiplot
set origin 0,0
set size 1,1
set border linewidth 1

set autoscale x
set autoscale y
set output 'gnuplot-figures/sigmetrics-fig-vm-types.eps'
set key vertical width 2 maxrows 10
set key at 10.2,0.73
set key spacing 1
set key font 'Helvetica, 24'
set xtics font "Helvetica, 24"
set ytics font "Helvetica, 24"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,24'
set ylabel 'CDF' font 'Helvetica,24'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.02]
plot \
'runtime-data-by-group/n1-highcpu-2.txt' u 1:2 every 1 t 'n1-highcpu-2' with p ls 10, \
'runtime-data-by-group/blended_exp_model/n1-highcpu-2.txt' u 1:2 every 3 notitle w l ls 15, \
'runtime-data-by-group/n1-highcpu-4.txt' u 1:2 every 1 t 'n1-highcpu-4' with p ls 11, \
'runtime-data-by-group/blended_exp_model/n1-highcpu-4.txt' u 1:2 every 4 notitle w l ls 16, \
'runtime-data-by-group/n1-highcpu-8.txt' u 1:2 every 1 t 'n1-highcpu-8' with p ls 13, \
'runtime-data-by-group/blended_exp_model/n1-highcpu-8.txt' u 1:2 every 5 notitle w l ls 18, \
'runtime-data-by-group/n1-highcpu-16.txt' u 1:2 every 1 t 'n1-highcpu-16' with p ls 12, \
'runtime-data-by-group/blended_exp_model/n1-highcpu-16.txt' u 1:2 every 5 notitle w l ls 17, \
'runtime-data-by-group/n1-highcpu-32.txt' u 1:2 every 1 t 'n1-highcpu-32' with p ls 14, \
'runtime-data-by-group/blended_exp_model/n1-highcpu-32.txt' u 1:2 every 3 notitle w l ls 19

set autoscale x
set autoscale y
set output 'gnuplot-figures/sigmetrics-time-breakdown.eps'
set key vertical width 2 maxrows 10
set key at 7, 0.7
set key spacing 1
set key font 'Helvetica, 24'
set xtics font "Helvetica, 24"
set ytics font "Helvetica, 24"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,24'
set ylabel 'CDF' font 'Helvetica,24'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.02]
plot \
'runtime-data-by-group/blended_exp_model/idle.txt' u 1:2 every 1 t 'Idle' with l ls 15 lw 3, \
'runtime-data-by-group/blended_exp_model/non-idle.txt' u 1:2 every 1 t 'Non-Idle' with l ls 21 lw 3 dashtype 2, \
'runtime-data-by-group/blended_exp_model/Night.txt' u 1:2 every 1 t 'Night' with l ls 19 dashtype 2, \
'runtime-data-by-group/blended_exp_model/Day.txt' u 1:2 every 1 t 'Day' with l ls 20

unset key

set autoscale x
set autoscale y
set output 'gnuplot-figures/sigmetrics-region-breakdown.eps'
set key vertical width 2 maxrows 10
set key at 9,0.8
set key samplen 3
set key spacing 1
set key font 'Helvetica, 24'
set xtics font "Helvetica, 24"
set ytics font "Helvetica, 24"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,24'
set ylabel 'CDF' font 'Helvetica,24'
set xlabel offset 0,0
set ylabel offset 0,0
#set xrange [0:25]
plot \
'runtime-data-by-group/blended_exp_model/us-central1-c.txt' u 1:2 every 3 with l ls 15 lw 3 dashtype 2 title 'us-central1-c', \
'runtime-data-by-group/blended_exp_model/us-central1-f.txt' u 1:2 every 3 with l ls 16 lw 3 title 'us-central1-f', \
'runtime-data-by-group/blended_exp_model/us-west1-a.txt' u 1:2 every 1 with l ls 14 lw 3 title 'us-west1-a', \
'runtime-data-by-group/blended_exp_model/us-east1-b.txt' u 1:2 every 5 with l ls 18 lw 3 dashtype 5  title 'us-east1-b'
	
unset key
	
exit 
