Configure
*********


Create the tourbillon-log configuration file
===============================================

You must create the tourbillon-log configuration file in order to use tourbillon-log.
By default, the configuration file must be placed in **/etc/tourbillon/conf.d** and its name
must be **log.conf**.

The tourbillon-log configuration file looks like: ::

	{
		"database": {
			"name": "log",
			"duration": "365d",
			"replication": "1"
		},
		"log_file": "/var/log/nginx/access.log",
		"measurements": "requests",
		"parser": {
			"regex": "([(\\d\\.)]+) - - \\[(.*?)\\] \"(.*?)\" (\\d+) (\\d+) \"(.*?)\" \"(.*?)\"",
			"mapping": [
				{
					"type": "field",
					"name": "source_ip",
					"idx": 0
				},
				{
					"type": "tag",
					"name": "user_agent",
					"idx": 6
				},
				{
					"type": "field",
					"name": "http_status",
					"idx": 3,
					"cast": "int"
				}
			]
		},
		"frecuency": 2
	}


You can customize the database name, the regular expression used to capture values, how each value is mapped against a field or a tag of the datapoint and the collecting interval.

Enable the tourbillon-log metrics collector
===========================================

To enable the tourbillon-log metrics collector types the following command: ::

	$ sudo -i tourbillon enable tourbillon.log=get_logfile_metrics


