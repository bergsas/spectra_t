tsu: Spectra T Series Utility
=============================

I want to make the management of our T950 tape library easier. By making 
a more or less generic command line front-end tool to the XML interface,
I hope to make management easier

Documentation
-------------
  * FEATURELESS.md -> features and non-features (a list of stuff from the ref)

Manifest
--------
  * bin/
    * tsu
      * The _t_ _s_eries _u_tility
    * spectra_t.py_
      * The spectra t library (will be moved away when I learn python)
  * testing/ 
    * includes some of the sample XML outputs from the lib ref.


Background
----------
Doing some research on our T950 I found the XML ref. And because I could not
find any other CLI utility (or indeed CLI), and because I don't like the whole
mouse clickety click thing of a web interface, I decided to make my life easier.
Especially access to the drivelist triggered this.

References
----------
  * T950 docs:
    * http://www.spectralogic.com/index.cfm?fuseaction=support.docsByProd&CatID=488
    * http://www.spectralogic.com/index.cfm?fuseaction=home.displayFile&DocID=283


  * T Series XML ref:
    * https://support.spectralogic.com/documentation/user-guides/spectra-t-series-libraries-xml-command-reference

Code references
---------------
  * Some curl stuff here:
    * http://pycurl.sourceforge.net/doc/quickstart.html
    * http://curl.haxx.se/docs/manpage.html

# vim:ft=markdown
