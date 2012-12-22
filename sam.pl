#!/usr/bin/perl

use strict;

use Class::Struct;
use Math::Spline qw(spline linsearch binsearch);
use Math::Derivative qw(Derivative2);

my $datapath = "./data";

struct Airfoil => {
    name => '$',
    description => '$',
    top_x => '@',
    top_y => '@',
    bottom_x => '@',
    bottom_y => '@',
};

# load airfoils
my $root_af = &airfoil_load( "clarky" );
my $tip_af = &airfoil_load( "arad6" );

# resample at a finer step size with (or without) spline interpolation
my $root_smooth = &airfoil_resample( $root_af, 1000, 1 );
my $tip_smooth = &airfoil_resample( $tip_af, 1000, 0 );

# blending airfoils requires identical size point arrays with matching
# "x" positions (thus the reason we smooth/resample the airfoils
# before blending them.)
my $blend1 = &airfoil_blend( $root_smooth, $tip_smooth, 1.0 );
my $blend2 = &airfoil_blend( $root_smooth, $tip_smooth, 0.5 );
my $blend3 = &airfoil_blend( $root_smooth, $tip_smooth, 0.0 );

# dump results
airfoil_print( $blend1 );
airfoil_print( $blend2 );
airfoil_print( $blend3 );


my $root_chord = 14.0;
# my $root_vert_scale = 1.0;

my $tip_chord = 10.0;
# my $tip_vert_scale = 1.0;

my $span = 48.0;
my $tip_offset = 6.0;
# my $twist_deg = 3.0;


sub airfoil_load {
    my $base = shift;

    my $airfoil = Airfoil->new();
    $airfoil->name($base);

    my $file = $datapath . "/airfoils/" . $base . ".dat";

    open( my $in, "<", "$file" ) || die "Cannot open $file\n";

    # first line is descriptive text (discard)
    my $desc = <$in>;
    # strip leading/trailing whitespace and collapse extra white space
    $desc =~ s/^\s+//;
    $desc =~ s/\s+$//;
    $desc =~ s/\s+/ /g;
    $airfoil->description($desc);

    # first half of data file is the top contour, when x = 0.0 that
    # marks the end of the top and the start of the bottom.
    my $top = 1;

    while ( <$in> ) {
	my $line = $_;
	$line =~ s/^\s+//;
	$line =~ s/\s+$//;
	my ($x, $y) = split(/\s+/, $line);
	if ( $top ) {
	    # print "top $x $y\n";
	    unshift $airfoil->top_x, $x;
	    unshift $airfoil->top_y, $y;
	} 

	# this if structure/order has the side effect of repeating the end
	# point as the start of the bottom contour
	if ( $x < 0.000001 ) {
	    $top = !$top;
	}

	if ( ! $top ) {
	    # print "bottom $x $y\n";
	    push $airfoil->bottom_x, $x;
	    push $airfoil->bottom_y, $y;
	}
    }

    my @tx = $airfoil->top_x;
    my @bx = $airfoil->bottom_x;
    printf( "loaded $desc ($base), top = %d points, bottom = %d points\n",
	    $#tx, $#bx);

    return ( $airfoil );
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


sub airfoil_resample {
    my $af_ref = shift;
    my $xdivs = shift;
    my $use_spline = shift;

    my $result = Airfoil->new();
    $result->name( $af_ref->name );
    $result->description( $af_ref->description );

    my $step = (1.0 / $xdivs);

    my @top_y2 = Derivative2( \@{$af_ref->top_x}, \@{$af_ref->top_y} );
    my @bottom_y2 = Derivative2( \@{$af_ref->bottom_x}, \@{$af_ref->bottom_y} );

    for ( my $i = 0; $i <= $xdivs; $i++ ) {
	my $x = $i * $step;

	my $index;
	my $y_interp;
	if ( $use_spline ) {
	    $index = binsearch(\@{$af_ref->top_x}, $x);
	    $y_interp = spline(\@{$af_ref->top_x}, \@{$af_ref->top_y}, \@top_y2, $index, $x);
	} else {
	    $y_interp = &simple_interp( \@{$af_ref->top_x}, \@{$af_ref->top_y}, $x );
	}

	push $result->top_x, $x;
	push $result->top_y, $y_interp;
    }

    for ( my $i = 0; $i <= $xdivs; $i++ ) {
	my $x = $i * $step;

	my $index;
	my $y_interp;
	if ( $use_spline ) {
	    $index = binsearch(\@{$af_ref->bottom_x}, $x);
	    $y_interp = spline(\@{$af_ref->bottom_x}, \@{$af_ref->bottom_y}, \@bottom_y2, $index, $x);
	} else {
	    $y_interp = &simple_interp( \@{$af_ref->bottom_x}, \@{$af_ref->bottom_y}, $x );
	}

	push $result->bottom_x, $x;
	push $result->bottom_y, $y_interp;
    }

    return $result;
}


sub airfoil_blend {
    my $af1_ref = shift;
    my $af2_ref = shift;
    my $percent = shift;

    my $result = Airfoil->new();
    $result->name( "blend $af1_ref->name $af2_ref->name" );
    $result->description( "blend " . $percent . " $af1_ref->description + "
			  . 1.0 - $percent . " $af2_ref->description ");
    
    my @top1_x = @{$af1_ref->top_x};
    my @top1_y = @{$af1_ref->top_y};
    my @top2_x = @{$af2_ref->top_x};
    my @top2_y = @{$af2_ref->top_y};
    my @bottom1_x = @{$af1_ref->bottom_x};
    my @bottom1_y = @{$af1_ref->bottom_y};
    my @bottom2_x = @{$af2_ref->bottom_x};
    my @bottom2_y = @{$af2_ref->bottom_y};

    for ( my $i = 0; $i <= $#top1_x; $i++ ) {
	my $y1 = $top1_y[$i];
	my $y2 = $top2_y[$i];

	my $y = $percent * $y1 + (1.0 - $percent) * $y2;

	push $result->top_x, $top1_x[$i];
	push $result->top_y, $y;
    }

    for ( my $i = 0; $i <= $#bottom1_x; $i++ ) {
	my $y1 = $bottom1_y[$i];
	my $y2 = $bottom2_y[$i];

	my $y = $percent * $y1 + (1.0 - $percent) * $y2;

	push $result->bottom_x, $bottom1_x[$i];
	push $result->bottom_y, $y;
    }

    return $result;
}


sub airfoil_print {
    my $af_ref = shift;

    my @top_x = @{$af_ref->top_x};
    my @top_y = @{$af_ref->top_y};
    my @bottom_x = @{$af_ref->bottom_x};
    my @bottom_y = @{$af_ref->bottom_y};

    for ( my $i = 0; $i <= $#top_x; $i++ ) {
	print "$top_x[$i] $top_y[$i]\n";
    }

    for ( my $i = 0; $i <= $#bottom_x; $i++ ) {
	print "$bottom_x[$i] $bottom_y[$i]\n";
    }

}
