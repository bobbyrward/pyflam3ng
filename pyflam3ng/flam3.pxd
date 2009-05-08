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

ctypedef unsigned long size_t


cdef extern from "string.h":
    void *memset(void *s, int c, size_t n)
    void *memmove(void *dest, void *src, size_t n)
    size_t strlen(char *s)
    char *strncpy(char *dest, char *src, size_t n)


cdef extern from "Python.h":
    int PyObject_AsWriteBuffer( object obj, void **buffer, Py_ssize_t *buffer_len)


cdef enum:
    c_flam3_nvariations = 82
    c_flam3_parent_fn_len = 30
    c_flam3_name_len = 64


cdef extern from "flam3.h":

    ctypedef struct flam3_palette_entry:
        double index
        double color[4]

    ctypedef flam3_palette_entry flam3_palette[256]

    char *flam3_variation_names[]

    ctypedef struct randctx:
        pass

    ctypedef struct flam3_img_comments:
        char *genome
        char *badvals
        char *numiters
        char *rtime

    ctypedef struct stat_struct:
       double badvals
       long num_iters
       int render_seconds

    ctypedef struct flam3_image_store:
       unsigned int width
       unsigned int height
       int version
       int id

       double intensity_weight[256]
       unsigned int bin_size[256]
       unsigned int bin_offset[256]

       unsigned short *rowcols

    ctypedef struct flam3_xform:
        double var[c_flam3_nvariations]
        double c[3][2]
        double post[3][2]
        double density
        double color[2]
        double symmetry

        int padding
        double wind[2]

        double blob_low
        double blob_high
        double blob_waves

        double pdj_a
        double pdj_b
        double pdj_c
        double pdj_d

        double fan2_x
        double fan2_y

        double rings2_val

        double perspective_angle
        double perspective_dist

        double juliaN_power
        double juliaN_dist

        double juliaScope_power
        double juliaScope_dist

        double radialBlur_angle

        double pie_slices
        double pie_rotation
        double pie_thickness

        double ngon_sides
        double ngon_power
        double ngon_circle
        double ngon_corners

        double curl_c1
        double curl_c2

        double rectangles_x
        double rectangles_y

        double amw_amp

        double disc2_rot
        double disc2_twist

        double supershape_rnd
        double supershape_m
        double supershape_n1
        double supershape_n2
        double supershape_n3
        double supershape_holes

        double flower_petals
        double flower_holes

        double conic_eccen
        double conic_holes

        double parabola_height
        double parabola_width

        double persp_vsin
        double persp_vfcos

        double juliaN_rN
        double juliaN_cn

        double juliaScope_rN
        double juliaScope_cn

        double radialBlur_spinvar
        double radialBlur_zoomvar

        double waves_dx2
        double waves_dy2

        double disc2_sinadd
        double disc2_cosadd
        double disc2_timespi

        double supershape_pm_4
        double supershape_pneg1_n1

#        int num_active_vars
#        double active_var_weights[flam3_nvariations]
#        int varFunc[flam3_nvariations]

    ctypedef struct flam3_genome:
        char flame_name[c_flam3_name_len+1]
        double time
        int interpolation
        int interpolation_type
        int palette_interpolation
        int num_xforms
        int final_xform_index
        int final_xform_enable
        flam3_xform *xform
        int genome_index
        char parent_fname[c_flam3_parent_fn_len]
        int symmetry
        flam3_palette palette
        char *input_image
        int  palette_index
        double brightness
        double contrast
        double gamma
        int  width, height
        int  spatial_oversample
        double center[2]
        double rot_center[2]
        double rotate
        double vibrancy
        double hue_rotation
        double background[3]
        double zoom
        double pixels_per_unit
        double spatial_filter_radius
        int spatial_filter_select
        double sample_density
        int nbatches
        int ntemporal_samples

        double estimator
        double estimator_curve
        double estimator_minimum

#        xmlDocPtr edits

        double gam_lin_thresh

        int palette_index0
        double hue_rotation0
        int palette_index1
        double hue_rotation1
        double palette_blend

        int temporal_filter_type
        double temporal_filter_width, temporal_filter_exp

    ctypedef struct flam3_frame:
        double         pixel_aspect_ratio
        flam3_genome  *genomes
        int            ngenomes
        int            verbose
        int            bits
        int            bytes_per_channel
        double         time
        int            (*progress)(void *, double, int, double)
        void          *progress_parameter
        randctx       rc
        int           nthreads
        int            earlyclip

    void *flam3_malloc(size_t size)
    void flam3_free(void *ptr)

#typedef void (*flam3_iterator)(void *, double)

    int flam3_get_palette(int palette_index, flam3_palette p, double hue_rotation) nogil
    void flam3_add_xforms(flam3_genome *cp, int num_to_add, int interp_padding, int final_flag) nogil
    void flam3_delete_xform(flam3_genome *thiscp, int idx_to_delete) nogil
    void flam3_copy(flam3_genome *dest, flam3_genome *src) nogil
    void flam3_copyx(flam3_genome *dest, flam3_genome *src, int num_std, int num_final) nogil
    void flam3_copy_params(flam3_xform *dest, flam3_xform *src, int varn) nogil
    void flam3_create_xform_distrib(flam3_genome *cp, unsigned short *xform_distrib) nogil
    int flam3_iterate(flam3_genome *g, int nsamples, int fuse, double *samples,
                         unsigned short *xform_distrib, randctx *rc) nogil
    void flam3_interpolate(flam3_genome *genomes, int ngenomes, double time, flam3_genome *result) nogil
    void flam3_interpolate_n(flam3_genome *result, int ncp, flam3_genome *cpi, double *c) nogil
    void flam3_print(void *f, flam3_genome *g, char *extra_attributes, int print_edits) nogil
    char *flam3_print_to_string(flam3_genome *cp) nogil
    void flam3_random(flam3_genome *g, int *ivars, int ivars_n, int sym, int spec_xforms) nogil
    flam3_genome *flam3_parse(char *s, int *ncps) nogil
    flam3_genome *flam3_parse_xml2(char *s, char *fn, int default_flag, int *ncps) nogil
    flam3_genome *flam3_parse_from_file(void *f, char *fn, int default_flag, int *ncps) nogil

    void flam3_add_symmetry(flam3_genome *g, int sym) nogil
    void flam3_parse_hexformat_colors(char *colstr, flam3_genome *cp, int numcolors, int chan) nogil

    void flam3_estimate_bounding_box(flam3_genome *g, double eps, int nsamples,
                 double *bmin, double *bmax, randctx *rc) nogil
    void flam3_rotate(flam3_genome *g, double angle, int interp_type) nogil
    void flam3_align(flam3_genome *dst, flam3_genome *src, int nsrc) nogil
    void establish_asymmetric_refangles(flam3_genome *cp, int ncps) nogil

    double flam3_dimension(flam3_genome *g, int ntries, int clip_to_camera) nogil
    double flam3_lyapunov(flam3_genome *g, int ntries) nogil

    void flam3_apply_template(flam3_genome *cp, flam3_genome *templ) nogil

    int flam3_count_nthreads() nogil
    void flam3_render(flam3_frame *f, void *out, int out_width, int field, int nchan, int transp, stat_struct *stats) nogil

    double flam3_render_memory_required(flam3_frame *f) nogil


    double flam3_random01() nogil
    double flam3_random11() nogil
    int flam3_random_bit() nogil

    double flam3_random_isaac_01(randctx *) nogil
    double flam3_random_isaac_11(randctx *) nogil
    int flam3_random_isaac_bit(randctx *) nogil

    void flam3_init_frame(flam3_frame *f) nogil

    size_t flam3_size_flattened_genome(flam3_genome *cp) nogil
    void flam3_flatten_genome(flam3_genome *cp, void *buf) nogil
    void flam3_unflatten_genome(void *buf, flam3_genome *cp) nogil

    void flam3_srandom() nogil

    void flam3_colorhist(flam3_genome *cp, int num_batches, double *hist) nogil


