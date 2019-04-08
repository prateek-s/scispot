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
set style line 10 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 2 pointsize 1 #for data
set style line 1 linecolor rgb 'red' linetype 2 linewidth 1 pointtype 6 pointsize 1
set style line 2 linecolor rgb 'green' linetype 3 linewidth 1 pointtype 6  pointsize 1
set style line 3 linecolor rgb 'blue' linetype 4 linewidth 1 pointtype 6 pointsize 1
set style line 4 linecolor rgb 'orange' linetype 5 linewidth 1 pointtype 6 pointsize 1
set style line 5 linecolor rgb 'black' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 6 linecolor rgb 'magenta' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 7 linecolor rgb 'brown' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 8 linecolor rgb 'purple' linetype 1 linewidth 1 pointtype 6  pointsize 1
set style line 9 linecolor rgb 'olive' linetype 1 linewidth 1 pointtype 6  pointsize 1

set tics nomirror

set fit quiet

# sets simulated
set1=1

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
cf5k = 1
cf5beta = 0.1
cf5alpha = 0.1
cf5b = 1

cf5(x) = cf5k * (x**cf5beta) * exp(cf5alpha*(x**cf5b))
fit cf5(x) 'data.out' u 1:2 via cf5k, cf5beta, cf5alpha, cf5b

dcf5(x) = cf5k * cf5beta * (x**(cf5beta-1)) * exp(cf5alpha*(x**cf5b)) * (1 + (cf5alpha*cf5b/cf5beta)* (x**cf5b))

print "Crevecoeur + SKJ params"
print "set", set1, "   ", cf5k, "  ", cf5beta, "  ", cf5alpha, cf5b
print "cf5(0)", cf5(0)

### new bath-tub inspired crevecouer (3 param)
cf4k = 1
cf4beta = 0.1
cf4alpha = 0.1

cf4(x) = cf4k * (x**cf4beta) * exp(cf4alpha*x)
fit cf4(x) 'data.out' u 1:2 via cf4k, cf4beta, cf4alpha

dcf4(x) = cf4k * cf4beta * (x**(cf4beta-1)) * exp(cf4alpha*x) * (1 + cf4alpha*x/cf4beta)

print "Crevecoeur fn params"
print "set", set1, "   ", cf4k, "  ", cf4beta, "  ", cf4alpha
print "cf4(0)", cf4(0)

## for analysis

set autoscale x
set autoscale y
set output 'fig-cdf-time.eps'
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
set yrange [0:1.2]
plot \
'data.out' u 1:2 every 1 t 'data' with p ls 10, \
f6(x) t 'Proposed Analytical Model' ls 5, \
pastf1(x) t 'Classical Exponential' ls 1, \
pastf2(x) t 'Classical Weibull' ls 2, \
cf4(x) t 'Bathtub-shaped failure rate model (Crevecoeur)' ls 3, \
cf5(x) t 'Crevecoeur+SKJ' ls 4

set autoscale x
set autoscale y
set output 'fig-prob-time.eps'
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
df6(x) t 'Proposed Analytical Model' ls 5, \
dpastf1(x) t 'Classical Exponential' ls 1, \
dpastf2(x) t 'Classical Weibull' ls 2, \
dcf4(x) t 'Bathtub-shaped failure rate model (Crevecoeur)' ls 3, \
dcf5(x) t 'Crevecoeur+SKJ' ls 4

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
pastf2(x) t 'Classical Weibull' ls 2

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
df6(x) t 'Proposed Analytical Model' ls 5, \
dpastf1(x) t 'Classical Exponential' ls 1, \
dpastf2(x) t 'Classical Weibull' ls 2

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