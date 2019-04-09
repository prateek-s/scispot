reset
set fontpath \
"/usr/share/texmf/fonts/type1/public/cm-super/" \
"/usr/share/texlive/texmf-dist/fonts/type1/public/amsfonts/cm/"
set terminal postscript eps enhanced color lw 1.5 dl 3.0 \
font 'Helvetica' \
fontfile 'cmmi10.pfb' \
fontfile 'cmr10.pfb' \
fontfile 'cmmib10.pfb' \
fontfile 'cmti10.pfb'
  
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
set style line 10 linecolor rgb 'red' linetype 1 linewidth 1 pointtype 6 pointsize 1 #for data
set style line 5 linecolor rgb 'black' linetype 1 linewidth 2 pointtype 6  pointsize 1
set style line 1 linecolor rgb 'brown' linetype 2 linewidth 2 pointtype 6 pointsize 1
set style line 3 linecolor rgb 'blue' linetype 4 linewidth 2 pointtype 6 pointsize 1

set style line 11 linecolor rgb 'blue' linetype 1 linewidth 1 pointtype 4 pointsize 1 #for data
set style line 12 linecolor rgb 'cyan' linetype 1 linewidth 1 pointtype 12 pointsize 1 #for data
set style line 13 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 8 pointsize 1 #for data
set style line 14 linecolor rgb 'black' linetype 1 linewidth 1 pointtype 10 pointsize 1 #for data

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
fit set2f(x) 'n1-highcpu-2.txt' u 1:2 via set2tau1, set2tau2, set2A, set2b

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
fit set4f(x) 'n1-highcpu-4.txt' u 1:2 via set4tau1, set4tau2, set4A, set4b

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
fit set8f(x) 'n1-highcpu-8.txt' u 1:2 via set8tau1, set8tau2, set8A, set8b

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
fit set16f(x) 'n1-highcpu-16.txt' u 1:2 via set16tau1, set16tau2, set16A, set16b

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

### past model exp (1 param)
pf1lambda = 1

pastf1(x) = (1 - exp(-x/pf1lambda))
fit pastf1(x) 'data.out' u 1:2 via pf1lambda

dpastf1(x) = (1/pf1lambda) * (exp(-x/pf1lambda))

print "Classical Exp params"
print "set", set1, "   ", pf1lambda
print "pastf1(0) ", pastf1(0)

### past model weibull (2 param)
pf2lambda = 1
pf2k = 1

pastf2(x) = (1 - exp(-(x/pf2lambda)**pf2k))
fit pastf2(x) 'data.out' u 1:2 via pf2lambda, pf2k

dpastf2(x) = (pf2k/pf2lambda) * exp(-(x/pf2lambda)**pf2k) * ((x/pf2lambda)**(pf2k-1))

print "Classical Weibull params"
print "set", set1, "   ", pf2lambda, "  ", pf2k
print "pastf2(0) ", pastf2(0)

### new crevecouer+SKJ (4 param)
#cf5k = 1
#cf5beta = 0.1
#cf5alpha = 0.1
#cf5b = 1

#cf5(x) = cf5k * (x**cf5beta) * exp(cf5alpha*(x**cf5b))
#fit cf5(x) 'data.out' u 1:2 via cf5k, cf5beta, cf5alpha, cf5b

#dcf5(x) = cf5k * cf5beta * (x**(cf5beta-1)) * exp(cf5alpha*(x**cf5b)) * (1 + (cf5alpha*cf5b/cf5beta)* (x**cf5b))

#print "Crevecoeur + SKJ params"
#print "set", set1, "   ", cf5k, "  ", cf5beta, "  ", cf5alpha, cf5b
#print "cf5(0)", cf5(0)

### new bath-tub inspired crevecouer (3 param)
#cf4k = 1
#cf4beta = 0.1
#cf4alpha = 0.1

#cf4(x) = cf4k * (x**cf4beta) * exp(cf4alpha*x)
#fit cf4(x) 'data.out' u 1:2 via cf4k, cf4beta, cf4alpha

#dcf4(x) = cf4k * cf4beta * (x**(cf4beta-1)) * exp(cf4alpha*x) * (1 + cf4alpha*x/cf4beta)

#print "Crevecoeur fn params"
#print "set", set1, "   ", cf4k, "  ", cf4beta, "  ", cf4alpha
#print "cf4(0)", cf4(0)

## for analysis

#set autoscale x
#set autoscale y
#set output 'fig-cdf-time.eps'
#set key vertical width 2 maxrows 10
#set key top left
##set key at 1e4,165
##set key samplen 2
#set key spacing 3
#set key font 'Helvetica, 18'
#set xtics font "Helvetica, 18"
#set ytics font "Helvetica, 18"
#set xtics offset 0,0
#set ytics offset 0,0
#set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
#set ylabel 'CDF' font 'Helvetica,20'
#set xlabel offset 0,0
#set ylabel offset 0,0
#set xrange [0:25]
#set yrange [0:1.2]
#plot \
#'data.out' u 1:2 every 1 t 'data' with p ls 10, \
#f6(x) t 'Proposed Analytical Model' ls 5, \
#pastf1(x) t 'Classical Exponential' ls 1, \
#pastf2(x) t 'Classical Weibull' ls 2, \
#cf4(x) t 'Bathtub-shaped failure rate model (Crevecoeur)' ls 3, \
#cf5(x) t 'Crevecoeur+SKJ' ls 4

#set autoscale x
#set autoscale y
#set output 'fig-prob-time.eps'
#set key vertical width 2 maxrows 10
#set key top left
##set key at 1e4,165
##set key samplen 2
#set key spacing 3
#set key font 'Helvetica, 18'
#set xtics font "Helvetica, 18"
#set ytics font "Helvetica, 18"
#set xtics offset 0,0
#set ytics offset 0,0
#set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
#set ylabel 'Probability' font 'Helvetica,20'
#set xlabel offset 0,0
#set ylabel offset 0,0
#set xrange [0:25]
#set yrange [0:1]
#plot \
#df6(x) t 'Proposed Analytical Model' ls 5, \
#dpastf1(x) t 'Classical Exponential' ls 1, \
#dpastf2(x) t 'Classical Weibull' ls 2, \
#dcf4(x) t 'Bathtub-shaped failure rate model (Crevecoeur)' ls 3, \
#dcf5(x) t 'Crevecoeur+SKJ' ls 4

## for paper

set autoscale x
set autoscale y
set output 'scispot-fig-cdf-time.eps'
set key vertical width 2 maxrows 10
set key top left
#set key at 1e4,165
#set key samplen 2
set key spacing 3
set key font 'Helvetica, 18'
set xtics font "Helvetica, 18"
set ytics font "Helvetica, 18"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
set ylabel 'CDF' font 'Helvetica,20'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.1]
plot \
'data.out' u 1:2 every 1 t 'data' with p ls 10, \
f6(x) t 'Proposed Model' ls 5, \
pastf1(x) t 'Classical Exponential' ls 1, \
pastf2(x) t 'Classical Weibull' ls 3

set autoscale x
set autoscale y
set output 'scispot-fig-prob-time.eps'
set key vertical width 2 maxrows 10
set key top left
#set key at 1e4,165
#set key samplen 2
set key spacing 3
set key font 'Helvetica, 18'
set xtics font "Helvetica, 18"
set ytics font "Helvetica, 18"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
set ylabel 'Probability' font 'Helvetica,20'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1]
plot \
df6(x) t 'Proposed Model' ls 5, \
dpastf1(x) t 'Classical Exponential' ls 1, \
dpastf2(x) t 'Classical Weibull' ls 3

set autoscale x
set autoscale y
set output 'scispot-fig-cdf-prob-inset-time.eps'
set multiplot
set origin 0,0
set size 1,1
set key vertical width 2 maxrows 10
set key bottom right
#set key at 1e4,165
#set key samplen 2
set key spacing 3
set key font 'Helvetica, 18'
set xtics font "Helvetica, 18"
set ytics font "Helvetica, 18"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
set ylabel 'CDF' font 'Helvetica,20'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.1]
plot \
'data.out' u 1:2 every 1 t 'Empirical Data' with p ls 10, \
f6(x) t 'Proposed Model' ls 5, \
pastf1(x) t 'Classical Exponential' ls 1, \
pastf2(x) t 'Classical Weibull' ls 3
#inset
set origin 0.11,0.565
set size 0.45, 0.42
set border linewidth 0.5
set autoscale x
set autoscale y
unset key
set xtics font "Helvetica, 14"
set ytics font "Helvetica, 14"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
unset xlabel
set ylabel 'Probability' font 'Helvetica,14'
set xlabel offset 0,0
set ylabel offset 2,0
set xrange [0:25]
set yrange [0:1]
plot \
df6(x) notitle ls 5, \
dpastf1(x) notitle ls 1, \
dpastf2(x) notitle ls 3

unset multiplot
set origin 0,0
set size 1,1
set border linewidth 1

set autoscale x
set autoscale y
set output 'scispot-fig-vm-types.eps'
set key vertical width 2 maxrows 10
set key top left
#set key at 1e4,165
#set key samplen 2
set key spacing 3
set key font 'Helvetica, 18'
set xtics font "Helvetica, 18"
set ytics font "Helvetica, 18"
set xtics offset 0,0
set ytics offset 0,0
set xlabel 'Time to Preemption (Hours)' font 'Helvetica,20'
set ylabel 'CDF' font 'Helvetica,20'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.1]
plot \
'n1-highcpu-2.txt' u 1:2 every 1 t 'n1-highcpu-2' with p ls 10, \
set2f(x) notitle ls 15, \
'n1-highcpu-4.txt' u 1:2 every 1 t 'n1-highcpu-4' with p ls 11, \
set4f(x) notitle ls 16, \
'n1-highcpu-8.txt' u 1:2 every 1 t 'n1-highcpu-8' with p ls 13, \
set8f(x) notitle ls 18, \
'n1-highcpu-16.txt' u 1:2 every 1 t 'n1-highcpu-16' with p ls 12, \
set16f(x) notitle ls 17, \
'n1-highcpu-32.txt' u 1:2 every 1 t 'n1-highcpu-32' with p ls 14, \
set32f(x) notitle ls 19

exit

## scratch
### new exponential weibull (3 param)
#ewf3lambda = 3
#ewf3k = 0.5
#ewf3alpha = 0.1

#ewf3(x) = (1 - exp(-(x/ewf3lambda)**ewf3k))**ewf3alpha
#fit ewf3(x) 'data.out' u 1:2 via ewf3lambda, ewf3k, ewf3alpha

#dewf3(x) = (ewf3alpha*ewf3k/ewf3lambda) * exp(-(x/ewf3lambda)**ewf3k) * ((x/ewf3lambda)**(ewf3k-1)) * ((1 - exp(-(x/ewf3lambda)**ewf3k))**(ewf3alpha-1)) 

#print "New Exp-Weibull params"
#print "set", set1, "   ", ewf3lambda, "  ", ewf3k, "  ", ewf3alpha
#print "ewf3(0)", ewf3(0)

## old work
###
#f1(x)=2*R*sinh((x-t0)/tau) + C

#R = 0.1
#C = 0.1
#t0 = 12.0
#tau = 1
#fit [0:] f1(x) 'data.out' u 1:2 via R, C, t0, tau

#df1(x) = 2*(R/tau)*cosh((x-t0)/tau)

#print "Elegant Sinh Fits"
#print "set", set1, "   ", R, "  ", t0, "  ", tau, "  ", C
###

### This is the most natural minimal model (4 param)
#A = 0.1
#B = 0.1
#tau1 = 2
#tau2 = 2
##f2C = 1

#f2(x) = A*(1 - exp(-x/tau1)) + B*(exp(x/tau2) - 1)
##f2(x) = A*(1 - exp(-x/tau1)) + B*(exp(x/tau2))
#fit [0:] f2(x) 'data.out' u 1:2 via A, B, tau1, tau2

#df2(x) = (A/tau1)*exp(-x/tau1) + (B/tau2)*exp(x/tau2)

#print "Natural Exp 4 param Fits"
#print "set", set1, "   ", A, "  ", B, "  ", tau1, "  ", tau2
#print "f2(0)", f2(0)
###

### Traditional form (fit to half time ~ 12 hours)

#f3(x) = f3A * (1 - exp(-x/f3tau1))
#fit [0:12] f3(x) 'data.out' u 1:2 via f3A, f3tau1

#df3(x) = (f3A/f3tau1) * exp(-x/f3tau1)

#print "Traditional (half) param Fits"
#print "set", set1, "   ", f3A, "  ", f3tau1
###

### Traditional form (full)

#f4(x) = f4A * (1 - exp(-x/f4tau1))
#fit [0:] f4(x) 'data.out' u 1:2 via f4A, f4tau1

#df4(x) = (f4A/f4tau1) * exp(-x/f4tau1)

#print "Traditional Fits"
#print "set", set1, "   ", f4A, "  ", f4tau1
###

### Simplify fit para meaning (4 param)
#f5A = 1
#f5b = 1
#f5tau1 = 1
#f5tau2 = 2

#f5(x) = f5A*(1-exp(-x/f5tau1)) + exp((x-f5b)/f5tau2)
#fit f5(x) 'data.out' u 1:2 via f5tau1, f5tau2, f5A, f5b

#df5(x) = (f5A/f5tau1)*exp(-x/f5tau1) + exp(-f5b/f5tau2)*(1/f5tau2)*exp(x/tau2)

#print "Natural Exp 4 param Fits"
#print "set", set1, "   ", f5A, "  ", f5tau1, "  ", f5tau2, "  ", f5b
#print "f5(0)", f5(0)
###