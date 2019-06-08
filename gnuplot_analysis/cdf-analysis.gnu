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

set fit quiet

# sets simulated
set1=0
set2=2
set4=4
set8=8
set16=16
set32=32

### Our model (4 param)
f6A = 1
f6b = 24
f6tau1 = 1
f6tau2 = 2

f6(x) = f6A*(1 - exp(-x/f6tau1) + exp((x-f6b)/f6tau2))
#f6(x) = 1 - exp(-x/f6tau1) + f6A*exp((x-f6b)/f6tau2)
fit f6(x) 'data.out' u 1:2 via f6tau1, f6tau2, f6A, f6b

df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set1, "   ", f6A, "  ", f6tau1, "  ", f6tau2, "  ", f6b
print "our f(0) ", f6(0)
###

# for 2
set2A = 1
set2b = 24
set2tau1 = 1
set2tau2 = 2

set2f(x) = set2A*(1 - exp(-x/set2tau1) + exp((x-set2b)/set2tau2))
fit set2f(x) 'night.txt' u 1:2 via set2tau1, set2tau2, set2A, set2b

#df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set2, "   ", set2A, "  ", set2tau1, "  ", set2tau2, "  ", set2b
print "our set2f(0) ", set2f(0)
###

# for 4
set4A = 1
set4b = 24
set4tau1 = 1
set4tau2 = 2

set4f(x) = set4A*(1 - exp(-x/set4tau1) + exp((x-set4b)/set4tau2))
fit set4f(x) 'day.txt' u 1:2 via set4tau1, set4tau2, set4A, set4b

#df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set4, "   ", set4A, "  ", set4tau1, "  ", set4tau2, "  ", set4b
print "our set4f(0) ", set4f(0)
###

# for 8
set8A = 1
set8b = 24
set8tau1 = 1
set8tau2 = 2

set8f(x) = set8A*(1 - exp(-x/set8tau1) + exp((x-set8b)/set8tau2))
fit set8f(x) '../data/runtime-data-by-group/idle.txt' u 1:2 via set8tau1, set8tau2, set8A, set8b

#df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set8, "   ", set8A, "  ", set8tau1, "  ", set8tau2, "  ", set8b
print "our set8f(0) ", set8f(0)
###


# for 16
set16A = 1
set16b = 24
set16tau1 = 1
set16tau2 = 2

set16f(x) = set16A*(1 - exp(-x/set16tau1) + exp((x-set16b)/set16tau2))
fit set16f(x) '../data/runtime-data-by-group/non-idle.txt' u 1:2 via set16tau1, set16tau2, set16A, set16b

#df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set16, "   ", set16A, "  ", set16tau1, "  ", set16tau2, "  ", set16b
print "our set16f(0) ", set16f(0)
###

# for 32
set32A = 1
set32b = 24
set32tau1 = 1
set32tau2 = 2

set32f(x) = set32A*(1 - exp(-x/set32tau1) + exp((x-set32b)/set32tau2))
fit set32f(x) 'n1-highcpu-32.txt' u 1:2 via set32tau1, set32tau2, set32A, set32b

#df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Our model params"
print "set", set32, "   ", set32A, "  ", set32tau1, "  ", set32tau2, "  ", set32b
print "our set32f(0) ", set32f(0)
###

set origin 0,0
set size 0.8,0.6
set border linewidth 1

set autoscale x
set autoscale y
set output 'time-breakdown.eps'
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
plot  set8f(x) with l ls 15 title 'Idle',\
set16f(x) with l ls 15 dashtype 3 title 'Non-idle', \
set2f(x) with l ls 19 dashtype 3 title 'Night', \
set4f(x) with l ls 19 title  'Day', \
 
exit

