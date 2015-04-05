# Visualizing the Wing Structure in 3D #

Modern computers are really good at drawing 3d renderings of objects.
And during the design process, being able to look at a 3d model of
your design, zoom in, zoom out, rotate, pan to look at it from all
angles is very valuable.

A fresh addition to MADesigner is the ability to create a 3d model of
the design with the exact parts in their exact locations which the
designer can look at.

# Details #

MADesigner can write out 3d models in a format called AC3D which is
associated with a 'shareware' 3d modeler by the same name.  The reason
ac3d format was chosen is because it is a simple ascii text format
that is easy to write.  And it is powerful enough to represent all the
objects we want to represent, including possible texturing in the
future.

AC3D models can be viewed with OSGViewer (which is an opensource tool)
or loaded into blender (and possibly even edited in blender and saved
as other formats) if you install the ac3d import/export plugin for
blender.

# Stations #

Wing ribs are located at "stations" along the span of a wing.  You can
define the actual station locations if you wish, or you can simply
define how many ribs you'd like and the code will space the stations
evenly across the span of the wing.

Stations are referred to by their distance from the root rib.  In the
above exampe we specify a control surface that spans station 17.0 to
station 28.0.  This design uses inches as the units so this is an 11
inch wide built up control surface.

# Hinge Line #

A very important aspect of built up control surfaces is the
requirement to have a straight hinge line.  (Think about it, curved
hinges do not work very well!)  The 'pos' parameter allows you to
define the front/back position of the start of the cutout (i.e. the
hinge line.)  You can specify a position that is some distance behind
the leading edge, some distance forward of the trailing edge, or at a
percentage point of the chord.

But what about wings (like this example) where following any of these
positions would lead to a curved hinge?  In addition to the above
positioning methods, you can also specify the position at the inner
station + a slope of the cutout, so you can put your hinge anywhere
you like in the wing and have it follow any angle line you like.

# Wedge Cutout #

The design/engineering approach to the control surfaces is to place
the hinge point at the top line of the wing.  The intension is to then
join the moveable control surface to the wing using a gapless hinge
scheme.  Gapless hinges are becoming much more popular and are quite
easy to attach and are quite robust when all the parts are engineered
with this scheme in mind.

You can specify the cutout/wedge angle (i.e. 30 degrees) and this then
defines the maximum downward deflection the surface can achieve.

Also notice that the main rib at the boundary of the control surface is shifted over by 1/2 the rib width and the matching control surface partial rib is shifted by 1/2 rib width in the opposing direction.  This makes everything fit and allows you to sheet or cover the entire cutout surface.

# Boundary Stringers #

The code automatically places boundary stringers at the hinge edges
(both top and bottom) so you as the builder have some structure to
attach your covering and hinge to (or to support sheeting if you are
building a fully or partially sheeted wing.)  Because with a gapless
hinge, the hinge load is spread across the entire length of the
surface, we can use much lighter materials around the hinge line and
don't need big blocks of balsa to anchor point hinges into.  This
saves on building, sanding, and weight, while allowing you to construct
complicated shapes with minimal sanding and use off the shelf stock
materials.

You may notice in the example wing that the top and bottom stringers for the control surface are not exactly parallel.  This is because we are cutting a fixed angle wedge out of a wing that has varying thickness. This means the control surface thickness changes along the span and the bottom line of the wedge cutout is not parallel to the top.

This is all computed and handled inside the code so you don't have to worry about it, but it's good to be aware and understand a bit of what is happenging under the hood.

## Example ##

![http://wiki.madesigner.googlecode.com/git/images/wing-3d-1.png](http://wiki.madesigner.googlecode.com/git/images/wing-3d-1.png)
![http://wiki.madesigner.googlecode.com/git/images/wing-3d-2.png](http://wiki.madesigner.googlecode.com/git/images/wing-3d-2.png)

# Code #

```
wing.build_ac3d( "sport-flyer" )
```

If you want to dump out the 3d model for your design, that's the one
line of code you need to add.