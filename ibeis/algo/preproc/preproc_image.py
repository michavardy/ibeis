import os
from os.path import splitext, basename, isabs
import warnings
import vtool_ibeis.exif as vtexif
import utool as ut
import six
(print, rrr, profile) = ut.inject2(__name__)


def parse_exif(pil_img):
    """ Image EXIF helper """
    exif_dict = vtexif.get_exif_dict(pil_img)
    # TODO: More tags
    # (mainly the orientation tag)
    lat, lon = vtexif.get_lat_lon(exif_dict)
    orient = vtexif.get_orientation(exif_dict, on_error='warn')
    time = vtexif.get_unixtime(exif_dict)
    return time, lat, lon, orient


def get_standard_ext(gpath):
    """ Returns standardized image extension """
    ext = splitext(gpath)[1].lower()
    return '.jpg' if ext == '.jpeg' else ext


@profile
def parse_imageinfo(gpath):
    """ Worker function: gpath must be in UNIX-PATH format!

    Args:
        gpath (str): image path

    Returns:
        tuple: param_tup -
            if successful returns a tuple of image parameters which are values
            for SQL columns on else returns None

    CommandLine:
        python -m ibeis.algo.preproc.preproc_image parse_imageinfo

    Doctest:
        >>> from ibeis.algo.preproc.preproc_image import *  # NOQA
        >>> gpath = ut.grab_test_imgpath('patsy.jpg')
        >>> param_tup = parse_imageinfo(gpath)
        >>> result = ('param_tup = %s' % (str(param_tup),))
        >>> print(result)
        >>> uuid = param_tup[0]
        >>> assert str(uuid) == '16008058-788c-2d48-cd50-f6029f726cbf'
    """
    # Try to open the image
    from PIL import Image
    import tempfile
    if six.PY2:
        import urlparse
        urlsplit = urlparse.urlsplit
    else:
        import urllib
        urlsplit = urllib.parse.urlsplit

    gpath = gpath.strip()

    url_protos = ['https://', 'http://']
    s3_proto = ['s3://']
    valid_protos = s3_proto + url_protos

    def isproto(gpath, valid_protos):
        return any(gpath.startswith(proto) for proto in valid_protos)

    def islocal(gpath):
        return not (isabs(gpath) and isproto(gpath, valid_protos))

    with warnings.catch_warnings(record=True) as w:
        try:
            if isproto(gpath, valid_protos):
                suffix = '.%s' % (basename(gpath), )
                temp_file, temp_filepath = tempfile.mkstemp(suffix=suffix)
                args = (gpath, temp_filepath, )
                print('[preproc] Caching remote %s file to temporary file %r' % args)

                if isproto(gpath, s3_proto):
                    s3_dict = ut.s3_str_decode_to_dict(gpath)
                    ut.grab_s3_contents(temp_filepath, **s3_dict)
                if isproto(gpath, url_protos):
                    # Ensure that the Unicode string is properly encoded for web requests
                    uri_ = urlsplit(gpath)
                    uri_path = six.moves.urllib.parse.quote(uri_.path.encode('utf8'))
                    uri_ = uri_._replace(path=uri_path)
                    uri_ = uri_.geturl()
                    six.moves.urllib.request.urlretrieve(uri_, filename=temp_filepath)
                gpath_ = temp_filepath
            else:
                temp_file, temp_filepath = None, None
                gpath_ = gpath

            # Open image with Exif support
            pil_img = Image.open(gpath_, 'r')
            # We cannot use pixel data as libjpeg is not determenistic (even for reads!)
            image_uuid = ut.get_file_uuid(gpath_)  # Read file ]-hash-> guid = gid
        except IOError as ex:
            print('[preproc] IOError: %s' % (str(ex),))
            return None
        if len(w) > 0:
            # for warn in w:
            #     warnings.showwarning(warn.message, warn.category,
            #                          warn.filename, warn.lineno, warn.file,
            #                          warn.line)
            #     warnstr = warnings.formatwarning
            #     print(warnstr)
            print('%d warnings issued by %r' % (len(w), gpath,))
    # Parse out the data
    width, height  = pil_img.size         # Read width, height
    time, lat, lon, orient = parse_exif(pil_img)  # Read exif tags
    if orient in [6, 8]:
        width, height = height, width
    #orig_gpath = gpath
    orig_gname = basename(gpath)
    ext = get_standard_ext(gpath)
    notes = ''
    # Build parameters tuple
    param_tup = (
        image_uuid,
        gpath,
        gpath,
        orig_gname,
        #orig_gpath,
        ext,
        width,
        height,
        time,
        lat,
        lon,
        orient,
        notes
    )

    if temp_filepath is not None:
        os.close(temp_file)
        os.unlink(temp_filepath)
    #print('[ginfo] %r %r' % (image_uuid, orig_gname))
    return param_tup


def on_delete(ibs, featweight_rowid_list, qreq_=None):
    print('Warning: Not Implemented')


if __name__ == '__main__':
    """
    python -m ibeis.algo.preproc.preproc_image
    python -m ibeis.algo.preproc.preproc_image --allexamples
    """
    import multiprocessing
    multiprocessing.freeze_support()
    import xdoctest
    xdoctest.doctest_module(__file__)
