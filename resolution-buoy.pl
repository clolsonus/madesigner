#!/usr/bin/perl

# model the ATI Resolution with all kinds of curvy stuff.

use strict;

use Math::Spline qw(spline linsearch binsearch);
use Math::Derivative qw(Derivative2);

# output configuration
#my $output_format = "ac3d";
#my $output_format = "data";
my $output_format = "slices";

my $slices = 16;
my $chops = 2000;
my $do_mirror = 1; # not working yet ....

# units in inches
my $total_width = 8.0;	# from centerline to outside of butt rib
my $front_length = 7.0; # from front tip of CS to leading edge of wing
my $rear_length = 2.5;  # from trailing edge of the wing to rear tip of CS
my $top_height = 0.5;   # from top of wing at butt rib to top of
			# center section at the center
my $total_depth = 4.4;  # total depth at deepest point at the center

my $chord_length = 15.0;

my $af_upper_factor = 0.06771; # portion of airfoil above incidence line
my $af_lower_factor = 0.03360; # portion of airfoil below incidence line
my $af_depth_factor = $af_upper_factor + $af_lower_factor;
                               # total airfoil depth factor
my $af_top_mid = 0.29605; # thickest point of top airfoil
my $af_bot_mid = 0.227765; # thickest point of bottom airfoil

my $butt_rib_top = $chord_length * $af_upper_factor;
my $butt_rib_bottom = -$chord_length * $af_lower_factor;
my $max_bottom = ($butt_rib_top + $top_height) - $total_depth;

my $wing_le_slope = 0.376; # about 20.586 deg: 38" width, 13deg
			   # trailing edge sweep, 13.5 root chord, 8
			   # tip chord.

my $quick_wing = 1; # generate a quick wing appendage
my $wing_panel_span = 38;
my $wing_tip_chord = 8;
my $wing_ribs = 9; # including butt and tip ribs
my $wing_thickness_factor = 0.2; # tip will be 1+this percent thicker
my $wing_te_sweep_deg = 13.0;
my $d2r = 0.017453293;
my $wing_washout_deg = 3;


my $steps = 100;
for ( my $i = 0; $i <= $steps; $i++ ) {
    my $x_lookup = (1.0 / $steps) * $i;
    my $y_interp = side_view_top_rear( $x_lookup );
    my $base = $total_depth - $top_height;
    #my $x = $x_lookup * $total_width * 0.5;
    #my $y = $y_interp * $base;
    #printf("%.8f %.8f\n", $x_lookup, $y_interp);
}
#exit


my @af_top_x;
my @af_top_y;
my @af_bottom_x;
my @af_bottom_y;

&load_airfoil_top( "airfoil-top" );
&load_airfoil_bottom( "airfoil-bottom" );

if ( $output_format eq "ac3d" ) {
    &gen_ac3d_headers();

}

my $step = 1.0 / $slices;

for ( my $i = 0; $i <= $slices; $i++ ) {
    my $x = $i * $step;

    # leading edge 
    my $y = top_view_nose( $x );
    my $fy = -$y * $front_length;
    # printf "%.4f %.4f\n", $x * $total_width, $fy;

    # trailing edge
    my $y = top_view_rear( $x );
    my $base = $front_length + $chord_length;
    my $ry = $y * $rear_length - $base - $rear_length;
    #printf( "%.4f %.4f\n", $x * $total_width, $ry );

    # top height
    my $y_interp = front_view_top( $x );
    my $ty = $butt_rib_top + $top_height - $y_interp * $top_height;
    #printf("%.8f %.8f\n", $x * $total_width, $ty);

    # bottom height
    my $range = $butt_rib_bottom - $max_bottom;
    my $by = $max_bottom;
    my $blend_factor = 0.0;
    my $blend_width = 0.6; # 0.5
    if ( $x >= (1.0 - $blend_width) ) {
	my $y_interp = front_view_bottom( ($x - (1.0-$blend_width)) / $blend_width );
	$blend_factor = $y_interp;
	$by = $y_interp * $range - $range + $butt_rib_bottom;
    }
    #printf("%.8f %.8f\n", $x * $total_width, $by);

    &render_slice( $fy, $ry, $ty, $by, $blend_factor, $x * $total_width );
}

if ( $quick_wing ) {
#my $quick_wing = 1; # generate a quick wing appendage
#my $wing_panel_span = 38;
#my $wing_tip_chord = 7;
#my $wing_thickness_factor = 1.2;
#my $wing_te_sweep_deg = 8.5;
#my $wing_washout_deg = 5;

    # leading edge butt
    my $y = top_view_nose( 1.0 );
    my $butt_fy = -$y * $front_length;
    # printf "%.4f %.4f\n", $x * $total_width, $fy;

    # trailing edge butt
    my $y = top_view_rear( 1.0 );
    my $base = $front_length + $chord_length;
    my $butt_ry = $y * $rear_length - $base - $rear_length;
    #printf( "%.4f %.4f\n", $x * $total_width, $ry );

    # tip trailing edge
    my $tip_offset = $wing_panel_span
	* sin($wing_te_sweep_deg*$d2r)/cos($wing_te_sweep_deg*$d2r);
    # print "tip trail = $trw\n";
    my $tip_ry = $butt_ry - $tip_offset;

    my $tip_fy = $tip_ry + $wing_tip_chord;

    my $front_dy = $butt_fy - $tip_fy;
    my $rear_dy = $butt_ry - $tip_ry;
    my $cy = 0; # center of airfoil

    my $span_step = $wing_panel_span / ($wing_ribs - 1);
    for ( my $i = 0; $i < $wing_ribs; $i++ ) {
	my $percent = $i / ($wing_ribs - 1);
	my $fy = $butt_fy - ($front_dy * $percent);
	my $ry = $butt_ry - ($rear_dy * $percent);
	# shift to zero nose point by subtracting $fy ( for Tim & Alibre )
	&render_airfoil( $fy - $butt_fy, $ry - $butt_fy, $cy, 1 + $wing_thickness_factor * $percent,
			 $total_width + ($wing_panel_span * $percent) );
    }
}

if ( $output_format eq "ac3d" ) {
    &gen_ac3d_surfaces();

}

# right butt rib
my $start = $front_length;
my $finish = $front_length + $chord_length;
for ( my $slice = $start; $slice < $finish; $slice += $step ) {
    #print "$slice 8.0\n";
}


sub simple_interp() {
    my $x = shift;
    my $y = shift;
    my $x_lookup = shift;

    my $index = binsearch($x, $x_lookup);
    my $size = @$x;
    #print("index = $index ($size)\n");
    if ( $index < @$x ) {
	my $xrange = $x->[$index+1] - $x->[$index];
	my $yrange = $y->[$index+1] - $y->[$index];
	#print(" xrange = $xrange\n");
	my $percent = ($x_lookup - $x->[$index]) / $xrange;
	#print(" percent = $percent\n");
	return $y->[$index] + $percent * $yrange;
    } else {
	return $y->[$index];
    }
}


sub simple_spline3 {
    my $x1 = shift(@_);
    my $y1 = shift(@_);
    my $slope1 = shift(@_);
    my $slope2 = shift(@_);
    my $x_lookup = shift(@_);

    my @x = (0.0, $x1, 1.0);
    my @y = (0.0, $y1, 1.0);
    my @y2 = Derivative2(\@x,\@y, $slope1, $slope2);

    my $index = binsearch(\@x, $x_lookup);
    my $y_interp = spline(\@x, \@y, \@y2, $index, $x_lookup);

    return $y_interp;
}


sub top_view_nose {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.25, 0.2, 0.0, $wing_le_slope, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub top_view_rear {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.5, 0.5, 0.0, 0.0, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub front_view_top {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.7, 0.45, 0.0, 1.5, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub front_view_bottom {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.5, 0.25, 0.0, 0.5, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub side_view_top_rear {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.5, 0.3, 0.0, 2.0, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub side_view_bottom_rear {
    my $x_lookup = shift;
    my $y_interp = simple_spline3( 0.7, 0.3, 0.0, 4.0, $x_lookup );
    #printf("%.3f %.3f\n", $x_lookup, $y_interp);
    return $y_interp;
}


sub load_airfoil_top {
    my $file = shift;
    open( my $in, "<", "$file" ) || die "Cannot open $file\n";
    while ( <$in> ) {
	my $line = $_;
	$line =~ s/^\s+//;
	$line =~ s/\s+$//;
	my ($x, $y) = split(/\s+/, $line);
	#print "$x $y\n";
	push @af_top_x, $x;
	push @af_top_y, $y;
    }
}


sub load_airfoil_bottom {
    my $file = shift;
    open( my $in, "<", "$file" ) || die "Cannot open $file\n";
    while ( <$in> ) {
	my $line = $_;
	$line =~ s/^\s+//;
	$line =~ s/\s+$//;
	my ($x, $y) = split(/\s+/, $line);
	#print "$x $y\n";
	push @af_bottom_x, $x;
	push @af_bottom_y, $y;
    }
}


# wrapper function to output a coordinate
sub output_coord {
    my $x = shift;
    my $y = shift;
    my $z = shift;

    if ( $output_format eq "slices" ) {
	printf( SLICEFD "%.8f,%.8f,%.8f\n", $x, $y, $z );
	#printf( SLICEFD "%.8f,%.8f\n", $x, $z );
    } else {
	printf( "%.8f %.8f %.8f\n", $x, $y, $z );
    }
}


sub render_slice {
    my $front = shift;
    my $rear = shift;
    my $top = shift;
    my $bottom = shift;
    my $blend_factor = shift;
    my $width = shift;

    my $longscale = $front - $rear;
    my $top_long_ctr = 0.0 - $front_length - $chord_length * $af_top_mid;
    my $bot_long_ctr = 0.0 - $front_length - $chord_length * $af_bot_mid;
    my $top_frontscale = $front - $top_long_ctr;
    my $bot_frontscale = $front - $bot_long_ctr;
    my $top_rearscale = $top_long_ctr - $rear;
    my $bot_rearscale = $bot_long_ctr - $rear;
    #print "front=$top_frontscale\n";

    my $max_top = $butt_rib_top + $top_height;
    my $max_vert_ctr = $max_top - ($total_depth) * ($af_upper_factor/$af_depth_factor);
    my $forward_prop = ($front_length + $front) / $front_length;
    my $vert_ctr = $forward_prop * $max_vert_ctr;

    my $vertscale = $top - $bottom;
    my $front_topscale = $top - $vert_ctr;
    my $front_bottomscale = $vert_ctr - $bottom;
    my $rear_topscale = $top;
    my $rear_bottomscale = -$bottom;

    my $step = (1.0 / $chops);
    my $topmid = int($af_top_mid / $step) * $step;
    my $bottommid = int($af_bot_mid / $step) * $step;

    if ( $output_format eq "slices" ) {
	&new_slice( "top", $width );
    }

    my @y2 = Derivative2(\@af_top_x,\@af_top_y);
    for ( my $i = 0; $i <= $chops; $i++ ) {
	my $x = $i * $step;

	if ( $x <= $topmid ) {
	    # top front
	    my $index = binsearch(\@af_top_x, $x);
	    my $y_interp = spline(\@af_top_x, \@af_top_y, \@y2, $index, $x);
	    my $y = ($y_interp / $af_upper_factor) * $front_topscale + $vert_ctr;
	    #printf "%.8f %.8f\n", $top_long_ctr + (1.0 - $x/$topmid) * $top_frontscale, $y;
	    output_coord( $top_long_ctr + (1.0 - $x/$topmid) * $top_frontscale,
			  $width, $y );
	} else {
	    # top rear

	    # compute ideal airfoil profile
	    my $index = binsearch(\@af_top_x, $x);
	    my $y_interp = spline(\@af_top_x, \@af_top_y, \@y2, $index, $x);
	    my $af_y = ($y_interp / $af_upper_factor) * $rear_topscale;
	    # printf "%.8f %.8f\n", $top_long_ctr - ($x-$topmid)/(1.0-$topmid) * $top_rearscale, $af_y;

	    # compute ideal center section profile
	    my $pos = ($x-$topmid)/(1.0-$topmid);
	    my $y_interp = side_view_top_rear( $pos );
	    my $top_y = $rear_topscale - $y_interp * $rear_topscale;
	    # printf "%.8f %.8f\n", $top_long_ctr - ($x-$topmid)/(1.0-$topmid) * $top_rearscale, $top_y;

	    my $range = $af_y - $top_y;
	    my $y = $range * $blend_factor + $top_y;
	    # printf "%.8f %.8f\n", $top_long_ctr - ($x-$topmid)/(1.0-$topmid) * $top_rearscale, $y;
	    output_coord( $top_long_ctr
			  - ($x-$topmid)/(1.0-$topmid) * $top_rearscale,
			  $width,
			  $y );
	}
    }

    if ( $output_format eq "slices" ) {
	&finish_slice();
    }

    if ( $output_format eq "slices" ) {
	&new_slice( "bottom", $width );
    }

    my @y2 = Derivative2(\@af_bottom_x,\@af_bottom_y);
    for ( my $i = 0; $i <= $chops; $i++ ) {
	my $x = $i * $step;

	if ( $x <= $bottommid ) {
	    # bottom front
	    my $index = binsearch(\@af_bottom_x, $x);
	    my $y_interp = spline(\@af_bottom_x, \@af_bottom_y, \@y2, $index, $x);
	    my $y = ($y_interp / $af_lower_factor) * $front_bottomscale + $vert_ctr;
	    # printf "%.8f %.8f\n", $bot_long_ctr + (1.0 - $x/$bottommid) * $bot_frontscale, $y;
	    output_coord( $bot_long_ctr + (1.0 - $x/$bottommid) * $bot_frontscale,
			  $width,
			  $y )
	} else {
	    # bottom rear
	    # compute ideal airfoil profile
	    my $index = binsearch(\@af_bottom_x, $x);
	    my $y_interp = spline(\@af_bottom_x, \@af_bottom_y, \@y2, $index, $x);
	    my $af_y = ($y_interp / $af_lower_factor) * $rear_bottomscale;
	    #printf "%.8f %.8f\n", $bot_long_ctr - ($x-$bottommid)/(1.0-$bottommid) * $bot_rearscale, $af_y;

	    # compute ideal center section profile
	    my $pos = ($x-$bottommid)/(1.0-$bottommid);
	    my $y_interp = side_view_bottom_rear( $pos );
	    my $bot_y = -$rear_bottomscale + $y_interp * $rear_bottomscale;
	    # printf "%.8f %.8f\n", $bot_long_ctr - ($x-$bottommid)/(1.0-$bottommid) * $bot_rearscale, $bot_y;

	    my $range = $af_y - $bot_y;
	    my $y = $range * $blend_factor + $bot_y;
	    # printf "%.8f %.8f\n", $bot_long_ctr - ($x-$bottommid)/(1.0-$bottommid) * $bot_rearscale, $y;
	    output_coord( $bot_long_ctr
			  - ($x-$bottommid)/(1.0-$bottommid) * $bot_rearscale,
			  $width,
			  $y );
        }
    }

    if ( $output_format eq "slices" ) {
	&finish_slice();
    }
}


sub render_airfoil {
    my $front = shift;
    my $rear = shift;
    my $centery = shift;
    my $factor = shift;
    my $width = shift;

    my $longscale = $front - $rear;

    my $step = (1.0 / $chops);

    if ( $output_format eq "slices" ) {
	&new_slice( "top", $width );
    }

    my @y2 = Derivative2(\@af_top_x,\@af_top_y);
    for ( my $i = 0; $i <= $chops; $i++ ) {
	my $x = $i * $step;

	# top
	my $index = binsearch(\@af_top_x, $x);
	my $y_interp = spline(\@af_top_x, \@af_top_y, \@y2, $index, $x);
	my $y = $y_interp * $longscale * $factor + $centery;
	#printf "%.8f %.8f\n", $top_long_ctr + (1.0 - $x/$topmid) * $top_frontscale, $y;
	output_coord( $front - $x * $longscale, $width, $y );
    }

    if ( $output_format eq "slices" ) {
	&finish_slice();
    }

    if ( $output_format eq "slices" ) {
	&new_slice( "bottom", $width );
    }

    my @y2 = Derivative2(\@af_bottom_x,\@af_bottom_y);
    for ( my $i = 0; $i <= $chops; $i++ ) {
	my $x = $i * $step;

	# bottom
	my $index = binsearch(\@af_bottom_x, $x);
	my $y_interp = spline(\@af_bottom_x, \@af_bottom_y, \@y2, $index, $x);
	my $y = $y_interp * $longscale * $factor + $centery;
	# printf "%.8f %.8f\n", $bot_long_ctr + (1.0 - $x/$bottommid) * $bot_frontscale, $y;
	output_coord( $front - $x * $longscale, $width, $y )
    }

    if ( $output_format eq "slices" ) {
	&finish_slice();
    }
}


sub gen_ac3d_headers() {
    print "AC3Db\n";
    print "MATERIAL \"res\" rgb 1 1 1 amb 1 1 1 emis 0 0 0 spec 0.2 0.2 0.2 shi 128 trans 0\n";
    print "OBJECT world\n";
    print "kids 1\n";
    print "OBJECT poly\n";
    print "name \"surface\"\n";
    my $numvert = ($slices + 1) * 2 * ($chops + 1);
    if ( $quick_wing ) {
	$numvert += 2 * ($chops + 1);
    }
    print "numvert $numvert\n";
}

sub gen_ac3d_surfaces() {
    my $numsurf = ($slices*2) * $chops;
    if ( $quick_wing ) {
	$numsurf += 2 * $chops;
    }

    print "numsurf $numsurf\n";
    for ( my $i = 0; $i < $slices; $i++ ) {
	my $start = $i * 2 * ($chops + 1);
	for ( my $j = 0; $j < $chops; $j++ ) {
	    my $pos = $start + $j;
	    print "SURF 0x10\n";
	    print "mat 0\n";
	    print "refs 4\n";
	    printf "%d 0 0\n", $pos;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1);	
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1) + 1;
	    printf "%d 0 0\n", $pos + 1;
	}
	for ( my $j = $chops + 1; $j < 2 * $chops + 1; $j++ ) {
	    my $pos = $start + $j;
	    print "SURF 0x10\n";
	    print "mat 0\n";
	    print "refs 4\n";
	    printf "%d 0 0\n", $pos;
	    printf "%d 0 0\n", $pos + 1;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1) + 1;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1);
	}
    }
    if ( $quick_wing ) {
	my $start = $slices * 2 * ($chops + 1);
	for ( my $j = 0; $j < $chops; $j++ ) {
	    my $pos = $start + $j;
	    print "SURF 0x10\n";
	    print "mat 0\n";
	    print "refs 4\n";
	    printf "%d 0 0\n", $pos;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1);	
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1) + 1;
	    printf "%d 0 0\n", $pos + 1;
	}
	for ( my $j = $chops + 1; $j < 2 * $chops + 1; $j++ ) {
	    my $pos = $start + $j;
	    print "SURF 0x10\n";
	    print "mat 0\n";
	    print "refs 4\n";
	    printf "%d 0 0\n", $pos;
	    printf "%d 0 0\n", $pos + 1;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1) + 1;
	    printf "%d 0 0\n", $pos + 2 * ($chops + 1);
	}
    }
}

sub gen_ac3d_footers() {
    print "kids 0\n";
}

sub new_slice() {
    my $base = shift;
    my $pos = shift;
    my $slice_file = sprintf("%s-%06.3f", $base, $pos);
    $slice_file =~ s/\./-/;
    open( SLICEFD, ">", "$slice_file.txt" ) || die "Cannot open $slice_file\n";
}

sub finish_slice() {
    close( SLICEFD );
}
