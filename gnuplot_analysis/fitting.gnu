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
set style line 5 linecolor rgb 'cyan' linetype 1 linewidth 1 pointtype 6  pointsize 1
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

set tics nomirror

set fit quiet

# sets simulated
set1=1

###
f1(x)=2*R*sinh((x-t0)/tau) + C

R = 0.1
C = 0.1
t0 = 12.0
tau = 1
fit [0:] f1(x) 'data.out' u 1:2 via R, C, t0, tau

df1(x) = 2*(R/tau)*cosh((x-t0)/tau)

print "Elegant Sinh Fits"
print "set", set1, "   ", R, "  ", t0, "  ", tau, "  ", C
###

### This is the most natural minimal model (4 param)
A = 0.1
B = 0.1
tau1 = 2
tau2 = 2
#f2C = 1

f2(x) = A*(1 - exp(-x/tau1)) + B*(exp(x/tau2) - 1)
#f2(x) = A*(1 - exp(-x/tau1)) + B*(exp(x/tau2))
fit [0:] f2(x) 'data.out' u 1:2 via A, B, tau1, tau2

df2(x) = (A/tau1)*exp(-x/tau1) + (B/tau2)*exp(x/tau2)

print "Natural Exp 4 param Fits"
print "set", set1, "   ", A, "  ", B, "  ", tau1, "  ", tau2
print "f2(0)", f2(0)
###

### Traditional form (fit to half time ~ 12 hours)

f3(x) = f3A * (1 - exp(-x/f3tau1))
fit [0:12] f3(x) 'data.out' u 1:2 via f3A, f3tau1

df3(x) = (f3A/f3tau1) * exp(-x/f3tau1)

print "Traditional (half) param Fits"
print "set", set1, "   ", f3A, "  ", f3tau1
###

### Traditional form (full)

f4(x) = f4A * (1 - exp(-x/f4tau1))
fit [0:] f4(x) 'data.out' u 1:2 via f4A, f4tau1

df4(x) = (f4A/f4tau1) * exp(-x/f4tau1)

print "Traditional Fits"
print "set", set1, "   ", f4A, "  ", f4tau1
###

### Simplify fit para meaning (4 param)
f5A = 1
f5b = 1
f5tau1 = 1
f5tau2 = 2

f5(x) = f5A*(1-exp(-x/f5tau1)) + exp((x-f5b)/f5tau2)
fit f5(x) 'data.out' u 1:2 via f5tau1, f5tau2, f5A, f5b

df5(x) = (f5A/f5tau1)*exp(-x/f5tau1) + exp(-f5b/f5tau2)*(1/f5tau2)*exp(x/tau2)

print "Natural Exp 4 param Fits"
print "set", set1, "   ", f5A, "  ", f5tau1, "  ", f5tau2, "  ", f5b
print "f5(0)", f5(0)
###


### Another refinement (4 param)
f6A = 1
f6b = 23
f6tau1 = 1
f6tau2 = 2

f6(x) = f6A*(1 - exp(-x/f6tau1) + exp((x-f6b)/f6tau2))
fit f6(x) 'data.out' u 1:2 via f6tau1, f6tau2, f6A, f6b

df6(x) = f6A * ( (1/f6tau1)*exp(-x/f6tau1) + (1/f6tau2)*exp((x-f6b)/f6tau2) )

print "Natural Exp 4 param Fits"
print "set", set1, "   ", f6A, "  ", f6tau1, "  ", f6tau2, "  ", f6b
print "f6(0)", f6(0)
###

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
set xlabel 'time' font 'Helvetica,20'
set ylabel 'cdf' font 'Helvetica,20'
set xlabel offset 0,0
set ylabel offset 0,0
set xrange [0:25]
set yrange [0:1.2]
plot \
'data.out' u 1:2 every 1 t 'data' with p ls 1, \
f1(x) t 'sinh form' ls 2, \
df1(x) t 'probability sinh' ls 12, \
f2(x) t 'exp form (4 param)' ls 3, \
df2(x) t 'probability (exp; 4 param)' ls 13, \
f5(x) t 'refine exp' ls 6, \
df5(x) t 'probability (refine exp; 4 param)' ls 16, \
f6(x) t 'more refined' ls 5, \
df6(x) t 'probability (more refined; 4 param)' ls 15
  
#f3(x) t 'traditional form (fit up to 12 hours)' ls 4, \
#df3(x) t 'probability (traditional half-window)' ls 14, \
#f4(x) t 'traditional form (fit to all)' ls 5, \
#df4(x) t 'probability (traditional full-window)' ls 15