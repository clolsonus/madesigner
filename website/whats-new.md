---
id: 60
title: 'What&#8217;s New'
date: 2013-12-20T19:24:47-06:00
author: Curtis Olson
layout: page
guid: http://madesigner.flightgear.org/?page_id=60
image: /wp-content/uploads/2013/12/wing-3d-1-672x372.png
---
# v0.5 &#8211; not yet released

  * Link your wing structures together to make multipanel wings.  For example a classic &#8220;polyhedral&#8221; glider wing.
  * Much improved (and far more buildable) control surface and hinge designs.
  * Support for flat stock trailing edges (similar to the guillows style wing builds.)
  * Vastly improved part nesting in the layout sheets.
  * I have actually used the program for some laser cut tests!  This is exciting. 🙂

# v0.4 &#8211; December 27, 2013

  * Control surfaces!  Specify the hinge line and the start/end station and your control surface is built automatically.  Supports multiple independant control surfaces per wing.
  * Version checking.  Alert if a newer version is available for download.
  * Warn if trying to build before all design changes have been saved.
  * Delete wings from previous design when opening a new design.
  * Spars are now always vertically aligned after rib is rotated for twist/washout.
  * Stringers are always aligned flush/tangent to the surface of the rib.
  * Saved .mad files (xml format) are now beautified rather than all stuffed together on a single line (better for version control or human editing.)
  * If asking to view the design in 3d, check if file is saved (clean) and built since last save.
  * Fix output of .svg (plans/templates/laser cutter sheets) so they are created in the same folder as the original .mad file.

# v0.3 &#8211; December 19, 2013

  * Add a suite of examples that illustrate many of the software&#8217;s capabilities.
  * Support for curved chord/taper wings.  This is done by defining a spline curve that evaluates to the chord at that point in the wing.   See docs and examples for more details.
  * Support for curved sweep wings.  This is probably a less useful feature, but is available nonetheless.  Instead of specifying a sweep angle, a spline curve can define the amount of forward/aft shift of the wing ribs relative to the span of the wing.  Again see the docs for specific explanation and examples.

# v0.2 &#8211; December 18, 2013

  * Add helper functions for selecting root and tip airfoils.
  * Support for separate size root and tip chords (allows generation of tapered wings.)
  * Changes to combo box trigger internal change detection.
  * Clean/dirty management, system suggest save if design is changed before quitting or loading a new design.
  * Deleted structures also make the model &#8216;dirty&#8217; (needs to be saved.)
  * Bug fixes.  (Found an edge case in the generation of 3d sheeting that was exposed on wings that blend from one airfoil to another.)

# v0.1 &#8211; December 15, 2013

  * Initial GUI front end interface to working back end build library.
  * Single .exe windows version via PyInstaller
  * InnoSetup setup packaging for Windows
  * Bug fixes when generating 3d model for wings with sweep and dihedral.
  * Integrated creator, builder, and viewer into single GUI.
  * Simple XML format for saving model designs.

# v0.05 (unreleased) &#8211; February 21, 2013

  * Switch to  using a polygon clipping library for many internal functions (making cutouts much more robust.)
  * Wing skinning
  * Shaped lightening holes (that follow the interior contour of the rib)
  * Support for &#8220;linked&#8221; wing panels (i.e. a polyhedral glider wing.)
  * Visualize the exact model that is generated in 3d.
  * Variety of bug fixes and clean ups.

# v0.0 (unreleased) &#8211; February 2, 2013

  * Initial revision
  * Airfoil blending, scaling, rotation
  * Smoothing, resampling, and adaptive fitting of airfoil curves
  * Cutting out basic shapes from airfoils for leading/trailing edges, spars, stringers, lightening holes, etc.
  * Best fit of leading edge cutout.
  * Best fit of trailing edge stock to airfoil shape.
  * Generates actual size build plans
  * Supports curved chord/taper function
  * Supports curved sweep function
  * Higher level function: cut flaps or ailerons into the wing structure.