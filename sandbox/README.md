# Designing Flitetest style foamboard wings

Skipping past the "why?" and jumping straight to how!

## Creating a simple rectangular wing

`$ python3 ft_wing2.py <chord_mm>`

This displays a matplotlib plot of the airfoil section, labeled with
dimensions.  Look at the console output for the cumulative dimensions
usedful for measuring out the wing by hand.  Since this is a
rectangular wing, just line up with one of the edges of your material
and measure out the wing width you want.  You can trim the wing tip to
suit, and mirror this process for the other wing half.

## Create wings with 2d plans

`$ python3 ft_wing2.py <root_chord_mm> <tip_chord_mm> <half_span_mm> <sweep_mm>`

This shows a plot of the two end profiles and a simplified plot of the
top down 2d cut lines.  It also creates a file called 'unfolded.svg'
which is a true scale svg file of your wing plan.  The svg can be
inported into inkscape or lightburn for further processing.

## Printing your plan on letter/a4 pages

1. Open the 'unfolded.svg' file in inkscape.
2. Print as a pdf (note where your file is saved, maybe in Documents?)
3. Install pdfposter (it is available as a package for fedora.)
4. Run `pdfposter -m letter -s 1 input.pdf output.pdf` (substitude a4 for letter if that is your preferred paper size.)
5. Print output.pdf (you may not need to print every page.)
6. Carefully align your pages and tape them together.  Tada!