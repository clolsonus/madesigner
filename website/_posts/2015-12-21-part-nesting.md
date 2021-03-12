---
id: 128
title: Part Nesting
date: 2015-12-21T15:43:24-06:00
author: Curtis Olson
layout: post
guid: http://madesigner.flightgear.org/?p=128
permalink: /tutorials/part-nesting/
image: /wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28-825x510.png
categories:
  - Tutorials
---
<a href="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28.png" rel="attachment wp-att-141"><img class="alignnone size-medium wp-image-141" src="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28-300x166.png" alt="Screenshot from 2015-12-29 18-29-28" width="300" height="166" srcset="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28-300x166.png 300w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28-768x424.png 768w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-29-18-29-28-1024x565.png 1024w" sizes="(max-width: 300px) 100vw, 300px" /></a>

One of the challenges when using rapid prototyping tools is laying out the parts on the cut sheet with minimal material waste.  This is actually quite a challenging problem to solve optimally, but there are strategies we can use to reach an acceptable part arrangement in a reasonable amount of time.

Here is how I achieved the nesting layout shown here.

  * I leveraged an open-source polygon clipping library which allows me to do operations on polygons.
  * Starting in the upper left corner, test place the next part.
  * Check if it overlaps the collective mask of already placed parts.
  * If it overlaps, move it down a small increment.  Repeat until we run over the bottom of the sheet.
  * If we still haven&#8217;t found a placement, shift over a small increment to the right and start back at the top.
  * Keep repeating until we find an open placement.  If we run out of sheet, start a new sheet.
  * When we place a part, add the mask (outline) of the part to the cumulative mask of all placed parts for that sheet.

Things I don&#8217;t do in the nesting algorithm:

  * I don&#8217;t mirror or rotate parts to get a better fit.
  * I don&#8217;t try different part orderings to get a better fit.
  * I don&#8217;t place in order by size.

There is room for improvement, but the results aren&#8217;t too bad.  If you are cutting one copy, this is probably just fine.

I cut this out on a laser cutter (using cardboard test material) and here&#8217;s how it looks &#8230; just exactly like the cut layout of course:

<a href="http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441.jpg" rel="attachment wp-att-130"><img class="alignnone size-medium wp-image-130" src="http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441-300x225.jpg" alt="IMG_20151221_150441" width="300" height="225" srcset="http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441-300x225.jpg 300w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441-768x576.jpg 768w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441-1024x768.jpg 1024w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/IMG_20151221_150441.jpg 1083w" sizes="(max-width: 300px) 100vw, 300px" /></a>

Watch the laser cutter working on the parts:

You may be curious what all these shapes make when the parts go together.  It is a flying wing design:

<a href="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29.png" rel="attachment wp-att-131"><img class="alignnone size-medium wp-image-131" src="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29-300x164.png" alt="Screenshot from 2015-12-21 15-14-29" width="300" height="164" srcset="http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29-300x164.png 300w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29-768x419.png 768w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29-1024x559.png 1024w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29-1200x655.png 1200w, http://madesigner.flightgear.org/wp-content/uploads/2015/12/Screenshot-from-2015-12-21-15-14-29.png 1600w" sizes="(max-width: 300px) 100vw, 300px" /></a>

This is just a test design I am using to work through various coding issues, but you might notice that the root airfoil is naca0021 and the tip airfoil is clarky.  The MAdesigner program smoothly blends from root to tip airfoils automatically.  This design also includes 5 degrees washout at the tip (blended smoothly from root to tip.)  And you may also notice the build tabs are located on the top of the airfoil.  This is a personal choice for this design &#8230; I think if I build it upside down, I will get a small bit of natural dihedral and it should look cool that way.