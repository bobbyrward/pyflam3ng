##############################################################################
#  The Combustion Flame Engine - pyflam3ng
#  http://combustion.sourceforge.net
#  http://github.com/bobbyrward/pyflam3ng/tree/master
#
#  Copyright (C) 2007-2008 by Bobby R. Ward <bobbyrward@gmail.com>
#
#  The Combustion Flame Engine is free software; you can redistribute
#  it and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation; either
#  version 3 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Library General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this library; see the file COPYING.LIB.  If not, write to
#  the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
#  Boston, MA 02111-1307, USA.
##############################################################################

import flam3
from lxml import etree

def load_flame(xml_source=None, fd=None, filename=None):
    if filename:
        fd = open(filename)

    try:
        if fd:
            xml_source = fd.read()
    finally:
        if filename:
            fd.close()

    tree = etree.fromstring(xml_source)
    genome_nodes = tree.xpath('//flame')

    return [Genome(flame_node=node) for node in genome_nodes]


def load_genome(flame_node=None, xml_source=None, genome_handle=None):
    if xml_source:
        flame_node = etree.fromstring(xml_source).xpath('//flame')[0]

    if flame_node:
        return Genome(flame_node=flame_node)
    elif genome_handle:
        return Genome(genome_handle=genome_handle)
    else:
        return None


class Genome(object):
    def __init__(self, flame_node=None, xml_source=None, genome_handle=None):
        initialization = """
        cp->palette_index = flam3_palette_random;
        cp->center[0] = 0.0;
        cp->center[1] = 0.0;
        cp->rot_center[0] = 0.0;
        cp->rot_center[1] = 0.0;
        cp->gamma = 4.0;
        cp->vibrancy = 1.0;
        cp->contrast = 1.0;
        cp->brightness = 4.0;
        cp->symmetry = 0;
        cp->hue_rotation = 0.0;
        cp->rotate = 0.0;
        cp->pixels_per_unit = 50;
        cp->interpolation = flam3_interpolation_linear;
        cp->palette_interpolation = flam3_palette_interpolation_hsv;

        cp->genome_index = 0;
        memset(cp->parent_fname,0,flam3_parent_fn_len);

        if (default_flag==flam3_defaults_on) {
           /* If defaults are on, set to reasonable values */
           cp->highlight_power = -1.0;
           cp->background[0] = 0.0;
           cp->background[1] = 0.0;
           cp->background[2] = 0.0;
           cp->width = 100;
           cp->height = 100;
           cp->spatial_oversample = 1;
           cp->spatial_filter_radius = 0.5;
           cp->zoom = 0.0;
           cp->sample_density = 1;
           /* Density estimation stuff defaulting to ON */
           cp->estimator = 9.0;
           cp->estimator_minimum = 0.0;
           cp->estimator_curve = 0.4;
           cp->gam_lin_thresh = 0.01;
    //       cp->motion_exp = 0.0;
           cp->nbatches = 1;
           cp->ntemporal_samples = 1000;
           cp->spatial_filter_select = flam3_gaussian_kernel;
           cp->interpolation_type = flam3_inttype_log;
           cp->temporal_filter_type = flam3_temporal_box;
           cp->temporal_filter_width = 1.0;
           cp->temporal_filter_exp = 0.0;
           cp->palette_mode = flam3_palette_mode_step;

        } else {
        """

    def _init_from_node(self, flame_node):
        self.flame_node = flame_node

    def _init_from_handle(self, genome_handle):
        self.genome_handle = genome_handle
        self._refresh_self_from_handle()

    def _refresh_handle_from_self(self):
        self.genome_handle = flam3.from_xml(etree.tostring(self.flame_node))

    def _refresh_self_from_handle(self):
        xml_source = flam3.to_xml(self.genome_handle)
        self.flame_node = etree.fromstring(xml_source).getroot()
        attrib = self.flame_node.attrib

        self.time = float(attrib.get('time', 0))
        self.width, self.height = map(int, attrib.get('size').split(' '))
        self.center_x, self.center_y = map(float, attrib.get('center').split(' '))
        self.pixels_per_unit = float(attrib.get('scale'))
        self.zoom = float(attrib.get('zoom', 0))
        self.rotate = float(attrib.get('rotate',

        self.interpolation = {
            'linear': flam3.flam3_interpolation_linear,
            'smooth': flam3.flam3_interpolation_smooth,
        }[attrib.get('interpolation', 'linear')]


        self.palette_interpolation = {
            'hsv': flam3.flam3_palette_interpolation_hsv,
            'sweep': flam3.flam3_palette_interpolation_sweep,
        }[attrib.get('palette_interpolation', 'hsv')]

flam3_node_attributes = """
   if (cp->flame_name[0]!=0)
      fprintf(f, " name=\"%s\"",cp->flame_name);

   fprintf(f, " rotate=\"%g\"", cp->rotate);
   fprintf(f, " supersample=\"%d\"", cp->spatial_oversample);
   fprintf(f, " filter=\"%g\"", cp->spatial_filter_radius);

   /* Need to print the correct kernel to use */
   if (cp->spatial_filter_select == flam3_gaussian_kernel)
      fprintf(f, " filter_shape=\"gaussian\"");
   else if (cp->spatial_filter_select == flam3_hermite_kernel)
      fprintf(f, " filter_shape=\"hermite\"");
   else if (cp->spatial_filter_select == flam3_box_kernel)
      fprintf(f, " filter_shape=\"box\"");
   else if (cp->spatial_filter_select == flam3_triangle_kernel)
      fprintf(f, " filter_shape=\"triangle\"");
   else if (cp->spatial_filter_select == flam3_bell_kernel)
      fprintf(f, " filter_shape=\"bell\"");
   else if (cp->spatial_filter_select == flam3_b_spline_kernel)
      fprintf(f, " filter_shape=\"bspline\"");
   else if (cp->spatial_filter_select == flam3_mitchell_kernel)
      fprintf(f, " filter_shape=\"mitchell\"");
   else if (cp->spatial_filter_select == flam3_blackman_kernel)
      fprintf(f, " filter_shape=\"blackman\"");
   else if (cp->spatial_filter_select == flam3_catrom_kernel)
      fprintf(f, " filter_shape=\"catrom\"");
   else if (cp->spatial_filter_select == flam3_hanning_kernel)
      fprintf(f, " filter_shape=\"hanning\"");
   else if (cp->spatial_filter_select == flam3_hamming_kernel)
      fprintf(f, " filter_shape=\"hamming\"");
   else if (cp->spatial_filter_select == flam3_lanczos3_kernel)
      fprintf(f, " filter_shape=\"lanczos3\"");
   else if (cp->spatial_filter_select == flam3_lanczos2_kernel)
      fprintf(f, " filter_shape=\"lanczos2\"");
   else if (cp->spatial_filter_select == flam3_quadratic_kernel)
      fprintf(f, " filter_shape=\"quadratic\"");

   if (cp->temporal_filter_type == flam3_temporal_box)
      fprintf(f, " temporal_filter_type=\"box\"");
   else if (cp->temporal_filter_type == flam3_temporal_gaussian)
      fprintf(f, " temporal_filter_type=\"gaussian\"");
   else if (cp->temporal_filter_type == flam3_temporal_exp)
      fprintf(f, " temporal_filter_type=\"exp\" temporal_filter_exp=\"%g\"",cp->temporal_filter_exp);

   fprintf(f, " temporal_filter_width=\"%g\"",cp->temporal_filter_width);



   fprintf(f, " quality=\"%g\"", cp->sample_density);
   fprintf(f, " passes=\"%d\"", cp->nbatches);
   fprintf(f, " temporal_samples=\"%d\"", cp->ntemporal_samples);
   fprintf(f, " background=\"%g %g %g\"",
      cp->background[0], cp->background[1], cp->background[2]);
   fprintf(f, " brightness=\"%g\"", cp->brightness);
   fprintf(f, " gamma=\"%g\"", cp->gamma);

   if (!flam27_flag)
      fprintf(f, " highlight_power=\"%g\"", cp->highlight_power);

   fprintf(f, " vibrancy=\"%g\"", cp->vibrancy);
   fprintf(f, " estimator_radius=\"%g\" estimator_minimum=\"%g\" estimator_curve=\"%g\"",
      cp->estimator, cp->estimator_minimum, cp->estimator_curve);
   fprintf(f, " gamma_threshold=\"%g\"", cp->gam_lin_thresh);

   if (flam3_palette_mode_step == cp->palette_mode)
      fprintf(f, " palette_mode=\"step\"");
   else if (flam3_palette_mode_linear == cp->palette_mode)
      fprintf(f, " palette_mode=\"linear\"");

   if (flam3_interpolation_linear != cp->interpolation)
       fprintf(f, " interpolation=\"smooth\"");

   if (flam3_inttype_linear == cp->interpolation_type)
       fprintf(f, " interpolation_type=\"linear\"");
   else if (flam3_inttype_log == cp->interpolation_type)
       fprintf(f, " interpolation_type=\"log\"");
   else if (flam3_inttype_compat == cp->interpolation_type)
       fprintf(f, " interpolation_type=\"old\"");
   else if (flam3_inttype_older == cp->interpolation_type)
       fprintf(f, " interpolation_type=\"older\"");


   if (flam3_palette_interpolation_hsv != cp->palette_interpolation)
       fprintf(f, " palette_interpolation=\"sweep\"");

   if (extra_attributes)
      fprintf(f, " %s", extra_attributes);

   fprintf(f, ">\n");

   if (cp->symmetry)
      fprintf(f, "   <symmetry kind=\"%d\"/>\n", cp->symmetry);
"""

