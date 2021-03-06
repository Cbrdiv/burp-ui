Gunicorn
========

Starting from v0.0.6, `Burp-UI`_ supports `Gunicorn`_ in
order to handle multiple users simultaneously because some operations (like the
online restoration) may take some time and thus may block any further requests.
With `Gunicorn`_, you have several workers that can proceed the requests so you
can handle more users.

You need to install ``gunicorn`` and ``gevent``:

::

    pip install gevent
    pip install gunicorn

You will then be able to launch `Burp-UI`_ this way:

::

    SERVER_SOFTWARE=gunicorn gunicorn -k gevent -w 4 'burpui:init(conf="/path/to/burpui.cfg")'


.. note:: The ``SERVER_SOFTWARE=gunicorn`` is mandatory

When using ``gunicorn``, the command line options are not available. Instead,
run the `Burp-UI`_ ``init`` method directly. Here are the parameters you can
play with:

- conf: Path to the `Burp-UI`_ configuration file
- verbose: Verbosity level between 0 and 4
- logfile: Path to a logfile in order to log `Burp-UI`_ internal messages

.. warning:: You **MUST** set the *appsecret* option in your configuration
             file when using gunicorn.
             The default *magic* value 'random' cannot be used. If you
             don't change the settings the default value will be 'none' and your
             cookies won't be secured.

Daemon
------

If you wish to run `Burp-UI`_ as a daemon process, the recommanded way is to use
`Gunicorn`_.

When installing the *gunicorn* package on debian, there is a handler script that
is able to start several instances of `Gunicorn`_ as daemons.

All you need to do is installing the *gunicorn* package and adding a
configuration file in */etc/gunicorn.d/*.

There is a sample configuration file available
`here <https://git.ziirish.me/ziirish/burp-ui/blob/master/contrib/gunicorn.d/burp-ui>`__.

If you are using this sample configuration file, make sure to create the
*burpui* user with the appropriate permissions first:

::

    # install the gunicorn package
    apt-get install gunicorn
    # copy the gunicorn sample configuration
    cp /usr/local/share/burpui/contrib/gunicorn.d/burp-ui /etc/gunicorn.d/
    # create the burpui user
    useradd -r -d /var/lib/burpui -c 'Burp-UI daemon user' burpui
    mkdir /etc/burp
    # copy the burp-ui sample configuration file
    cp /usr/local/share/burpui/etc/burpui.sample.cfg /etc/burp/burpui.cfg
    mkdir -p /var/log/gunicorn
    chown -R burpui: /var/log/gunicorn


You will also need a custom client configuration and you will have to create the
certificates accordingly:

::

    # create the configuration file used by burp-ui
    cat >/var/lib/burpui/burp.conf<<EOF
    mode = client
    port = 4971
    status_port = 4972
    server = 127.0.0.1
    password = abcdefgh
    cname = bui-agent1
    pidfile = /var/lib/burpui/bui-agent1.client.pid
    syslog = 0
    stdout = 1
    progress_counter = 1
    ca_burp_ca = /usr/sbin/burp_ca
    ca_csr_dir = /var/lib/burpui/CA-client
    ssl_cert_ca = /var/lib/burpui/ssl_cert_ca.pem
    ssl_cert = /var/lib/burpui/ssl_cert-client.pem
    ssl_key = /var/lib/burpui/ssl_cert-client.key
    ssl_peer_cn = burpserver
    EOF
    # generate the certificates
    burp_ca --name bui-agent1 --ca burpCA --key --request --sign --batch
    cp /etc/burp/ssl_cert_ca.pem /var/lib/burpui/
    cp -a /etc/burp/CA/bui-agent1.crt /var/lib/burpui/ssl_cert-client.pem
    cp -a /etc/burp/CA/bui-agent1.key /var/lib/burpui/ssl_cert-client.key
    chown -R burpui: /var/lib/burpui/


Now you need to add the *bui-agent1* client to the authorized clients:

::

    echo "password = abcdefgh" >/etc/burp/clientconfdir/bui-agent1
    echo "restore_client = bui-agent1" >>/etc/burp/burp-server.conf


Finally, make sure you set ``bconfcli: /var/lib/burpui/burp.conf`` in your 
`Burp-UI`_ configuration filei (*/etc/burp/burpui.cfg*), and then you can
restart `Gunicorn`_:

::

    service gunicorn restart


If you want to take advantage of *advanced* features such as client add/removal
and configuration files edition, you should set the permissions accordingly
Burp-side.

First of all, add the following lines in your */etc/burp/burp-server.conf*:

::

    user = burpui
    group = burpui


Then you need to fix some permissions:

::

    chown -R burpui: /etc/burp/{burp-server.conf,burpui.cfg,CA,CA.cnf,clientconfdir,dhfile.pem,ssl_cert_ca.pem,ssl_cert-server.key,ssl_cert-server.pem} /var/spool/burp
    chgrp burpui /etc/burp
    chmod g+rwx /etc/burp


Finally you can restart your ``burp-server``.

.. note:: The above commands are meant for *default* setup, you may need to
          adapt the paths.

Reverse-Proxy
-------------

You may want to add a reverse-proxy so `Burp-UI`_ can be accessed on port 80 (or
443) along with other applications.

Here is a sample configuration for Nginx:

::

    server {
        listen 80;
        server_name burpui.example.com;

        access_log  /var/log/nginx/burpui.access.log;
        error_log   /var/log/nginx/burpui.error.log;

        location / {

            # you need to change this to "https", if you set "ssl" directive to "on"
            proxy_set_header   X-FORWARDED_PROTO http;
            proxy_set_header   Host              $http_host;
            proxy_set_header   X-Forwarded-For   $remote_addr;

            proxy_read_timeout 300;
            proxy_connect_timeout 300;

            proxy_pass http://localhost:5000;
        }
    }


Sub-root path
^^^^^^^^^^^^^

You can host `Burp-UI`_ behind a sub-root path. For instance ``/burpui``.
To accomplish this, you can either setup your reverse-proxy to announce the
desired *prefix*, or you can use the ``prefix`` option in your `Burp-UI`_
configuration file (see `usage <usage.html>`_ for details).

If you want to configure this reverse-proxy side, you need to announce the HTTP
Header ``X-Script-Name``.

Here is a sample configuration for Nginx:

::

    server {
        listen 80;
        server_name example.com;

        access_log  /var/log/nginx/burpui.access.log;
        error_log   /var/log/nginx/burpui.error.log;

        location /burpui {

            # you need to change this to "https", if you set "ssl" directive to "on"
            proxy_set_header   X-FORWARDED_PROTO http;
            proxy_set_header   Host              $http_host;
            proxy_set_header   X-Forwarded-For   $remote_addr;
            # Our service is hosted behind the "/burpui" prefix
            proxy_set_header   X-Script-Name     /burpui;

            proxy_read_timeout 300;
            proxy_connect_timeout 300;

            proxy_pass http://localhost:5000;
        }
    }


Apache sample:

::

    ProxyPass /burp/ http://localhost:5000/burp/
    ProxyPassReverse /burp/ http://localhost:5000/burp/
    <Location /burp/>
        SetOutputFilter proxy-html
        ProxyPassReverse /burp/
        ProxyHTMLURLMap  http://localhost:5000/     /
        Require all granted
    </Location>


.. warning:: If your *prefix* does not start with a '/', it will be ignored.

Production
----------

We can consider the `demo`_ as a production example of what you can setup/expect
in your environment.
It is using `Gunicorn`_ along with Nginx as described above.

In order to improve performances, `Redis`_ can be used to cache sessions and
various API calls.

See the `production <usage.html#production>`_ section of the
`usage <usage.html>`_ page.

.. _Gunicorn: http://gunicorn.org/
.. _Burp-UI: https://git.ziirish.me/ziirish/burp-ui
.. _demo: https://demo.ziirish.me/
.. _Redis: http://redis.io/
