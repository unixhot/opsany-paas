default_monitor_dashboard_dict = {
    "annotations": {
        "list": [{
            "builtIn": 1,
            "datasource": "-- Grafana --",
            "enable": True,
            "hide": True,
            "iconColor": "rgba(0, 211, 255, 1)",
            "name": "Annotations & Alerts",
            "type": "dashboard"
        }]
    },
    "editable": True,
    "gnetId": None,
    "graphTooltip": 0,
    "iteration": 1624090105323,
    "links": [],
    "panels": [{
            "aliasColors": {
                "CPU iowait time": "#B7DBAB",
                "CPU system time": "#BF1B00",
                "CPU user time": "#EAB839"
            },
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": "Zabbix",
            "description": "CPU使用率",
            "editable": True,
            "error": False,
            "fieldConfig": {
                "defaults": {
                    "custom": {}
                },
                "overrides": []
            },
            "fill": 3,
            "fillGradient": 0,
            "grid": {},
            "gridPos": {
                "h": 8,
                "w": 12,
                "x": 0,
                "y": 0
            },
            "hiddenSeries": False,
            "id": 1,
            "legend": {
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "show": True,
                "total": False,
                "values": False
            },
            "lines": True,
            "linewidth": 1,
            "links": [],
            "NonePointMode": "connected",
            "options": {
                "alertThreshold": True
            },
            "percentage": False,
            "pluginVersion": "7.3.5",
            "pointradius": 2,
            "points": False,
            "renderer": "flot",
            "seriesOverrides": [],
            "spaceLength": 10,
            "stack": True,
            "steppedLine": False,
            "targets": [{
                "application": {
                    "filter": "CPU"
                },
                "countTriggers": True,
                "functions": [],
                "group": {
                    "filter": "$group"
                },
                "host": {
                    "filter": "$host"
                },
                "item": {
                    "filter": "/CPU/"
                },
                "minSeverity": 3,
                "options": {
                    "disableDataAlignment": False,
                    "showDisabledItems": False,
                    "skipEmptyValues": False
                },
                "proxy": {
                    "filter": ""
                },
                "queryType": 0,
                "refId": "A",
                "resultFormat": "time_series",
                "table": {
                    "skipEmptyValues": False
                },
                "tags": {
                    "filter": ""
                },
                "trigger": {
                    "filter": ""
                },
                "triggers": {
                    "acknowledged": 2,
                    "count": True,
                    "minSeverity": 3
                }
            }],
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "title": "CPU使用率",
            "tooltip": {
                "msResolution": False,
                "shared": True,
                "sort": 0,
                "value_type": "individual"
            },
            "type": "graph",
            "xaxis": {
                "buckets": None,
                "mode": "time",
                "name": None,
                "show": True,
                "values": []
            },
            "yaxes": [{
                    "format": "percent",
                    "logBase": 1,
                    "max": 100,
                    "min": 0,
                    "show": True
                },
                {
                    "format": "short",
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                }
            ],
            "yaxis": {
                "align": False,
                "alignLevel": None
            }
        },
        {
            "aliasColors": {},
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": None,
            "description": "内存使用率",
            "fieldConfig": {
                "defaults": {
                    "custom": {}
                },
                "overrides": []
            },
            "fill": 1,
            "fillGradient": 0,
            "gridPos": {
                "h": 8,
                "w": 12,
                "x": 12,
                "y": 0
            },
            "hiddenSeries": False,
            "id": 7,
            "legend": {
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "show": True,
                "total": False,
                "values": False
            },
            "lines": True,
            "linewidth": 1,
            "NonePointMode": "None",
            "options": {
                "alertThreshold": True
            },
            "percentage": False,
            "pluginVersion": "7.3.5",
            "pointradius": 2,
            "points": False,
            "renderer": "flot",
            "seriesOverrides": [],
            "spaceLength": 10,
            "stack": False,
            "steppedLine": False,
            "targets": [{
                "application": {
                    "filter": "Memory"
                },
                "functions": [],
                "group": {
                    "filter": "Opsany_Group"
                },
                "host": {
                    "filter": "$host"
                },
                "item": {
                    "filter": "Available memory in %"
                },
                "options": {
                    "disableDataAlignment": False,
                    "showDisabledItems": False,
                    "skipEmptyValues": False
                },
                "proxy": {
                    "filter": ""
                },
                "queryType": 0,
                "refId": "A",
                "resultFormat": "time_series",
                "table": {
                    "skipEmptyValues": False
                },
                "tags": {
                    "filter": ""
                },
                "trigger": {
                    "filter": ""
                },
                "triggers": {
                    "acknowledged": 2,
                    "count": True,
                    "minSeverity": 3
                }
            }],
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "title": "内存使用率",
            "tooltip": {
                "shared": True,
                "sort": 0,
                "value_type": "individual"
            },
            "type": "graph",
            "xaxis": {
                "buckets": None,
                "mode": "time",
                "name": None,
                "show": True,
                "values": []
            },
            "yaxes": [{
                    "format": "percent",
                    "label": None,
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                },
                {
                    "format": "short",
                    "label": None,
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                }
            ],
            "yaxis": {
                "align": False,
                "alignLevel": None
            }
        },
        {
            "aliasColors": {
                "Processor load (1 min average per core)": "#1F78C1"
            },
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": "Zabbix",
            "description": "系统负载",
            "editable": True,
            "error": False,
            "fieldConfig": {
                "defaults": {
                    "custom": {}
                },
                "overrides": []
            },
            "fill": 1,
            "fillGradient": 0,
            "grid": {},
            "gridPos": {
                "h": 9,
                "w": 12,
                "x": 0,
                "y": 8
            },
            "hiddenSeries": False,
            "id": 2,
            "legend": {
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "show": True,
                "total": False,
                "values": False
            },
            "lines": True,
            "linewidth": 2,
            "links": [],
            "NonePointMode": "connected",
            "options": {
                "alertThreshold": True
            },
            "percentage": False,
            "pluginVersion": "7.3.5",
            "pointradius": 5,
            "points": False,
            "renderer": "flot",
            "seriesOverrides": [],
            "spaceLength": 10,
            "stack": False,
            "steppedLine": False,
            "targets": [{
                "application": {
                    "filter": "CPU"
                },
                "countTriggers": True,
                "functions": [],
                "group": {
                    "filter": "$group"
                },
                "host": {
                    "filter": "$host"
                },
                "item": {
                    "filter": "Load average (5m avg)"
                },
                "minSeverity": 3,
                "options": {
                    "disableDataAlignment": False,
                    "showDisabledItems": False,
                    "skipEmptyValues": False
                },
                "proxy": {
                    "filter": ""
                },
                "queryType": 0,
                "refId": "A",
                "resultFormat": "time_series",
                "table": {
                    "skipEmptyValues": False
                },
                "tags": {
                    "filter": ""
                },
                "trigger": {
                    "filter": ""
                },
                "triggers": {
                    "acknowledged": 2,
                    "count": True,
                    "minSeverity": 3
                }
            }],
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "title": "系统负载",
            "tooltip": {
                "msResolution": False,
                "shared": True,
                "sort": 0,
                "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
                "buckets": None,
                "mode": "time",
                "name": None,
                "show": True,
                "values": []
            },
            "yaxes": [{
                    "format": "short",
                    "logBase": 1,
                    "max": None,
                    "min": 0,
                    "show": True
                },
                {
                    "format": "short",
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                }
            ],
            "yaxis": {
                "align": False,
                "alignLevel": None
            }
        },
        {
            "aliasColors": {},
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": "Zabbix",
            "description": "网卡流量",
            "editable": True,
            "error": False,
            "fieldConfig": {
                "defaults": {
                    "custom": {}
                },
                "overrides": []
            },
            "fill": 3,
            "fillGradient": 0,
            "grid": {},
            "gridPos": {
                "h": 9,
                "w": 12,
                "x": 12,
                "y": 8
            },
            "hiddenSeries": False,
            "id": 3,
            "legend": {
                "alignAsTable": False,
                "avg": False,
                "current": False,
                "max": False,
                "min": False,
                "rightSide": False,
                "show": True,
                "total": False,
                "values": False
            },
            "lines": True,
            "linewidth": 2,
            "links": [],
            "maxPerRow": 3,
            "NonePointMode": "connected",
            "options": {
                "alertThreshold": True
            },
            "percentage": False,
            "pluginVersion": "7.3.5",
            "pointradius": 5,
            "points": False,
            "renderer": "flot",
            "repeat": "netif",
            "seriesOverrides": [{
                "alias": "/Incoming/",
                "transform": "negative-Y"
            }],
            "spaceLength": 10,
            "stack": False,
            "steppedLine": False,
            "targets": [{
                "application": {
                    "filter": ""
                },
                "countTriggers": True,
                "functions": [],
                "group": {
                    "filter": "$group"
                },
                "host": {
                    "filter": "$host"
                },
                "item": {
                    "filter": "/$netif/"
                },
                "minSeverity": 3,
                "options": {
                    "disableDataAlignment": False,
                    "showDisabledItems": False,
                    "skipEmptyValues": False
                },
                "proxy": {
                    "filter": ""
                },
                "queryType": 0,
                "refId": "A",
                "resultFormat": "time_series",
                "table": {
                    "skipEmptyValues": False
                },
                "tags": {
                    "filter": ""
                },
                "trigger": {
                    "filter": ""
                },
                "triggers": {
                    "acknowledged": 2,
                    "count": True,
                    "minSeverity": 3
                }
            }],
            "thresholds": [],
            "timeFrom": None,
            "timeRegions": [],
            "timeShift": None,
            "title": "网卡流量",
            "tooltip": {
                "msResolution": False,
                "shared": True,
                "sort": 0,
                "value_type": "cumulative"
            },
            "type": "graph",
            "xaxis": {
                "buckets": None,
                "mode": "time",
                "name": None,
                "show": True,
                "values": []
            },
            "yaxes": [{
                    "format": "bytes",
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                },
                {
                    "format": "short",
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                }
            ],
            "yaxis": {
                "align": False,
                "alignLevel": None
            }
        },
        {
            "collapsed": False,
            "datasource": None,
            "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 17
            },
            "id": 4,
            "panels": [],
            "repeat": None,
            "title": "CPU",
            "type": "row"
        },
        {
            "collapsed": False,
            "datasource": None,
            "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 18
            },
            "id": 5,
            "panels": [],
            "repeat": None,
            "title": "Network",
            "type": "row"
        }
    ],
    "revision": 1,
    "schemaVersion": 27,
    "style": "dark",
    "tags": [
        "zabbix",
        "example"
    ],
    "templating": {
        "list": [{
                "allFormat": "regex values",
                "allValue": None,
                "current": {
                    "selected": False,
                    "text": "Opsany_Group",
                    "value": "Opsany_Group"
                },
                "datasource": "Zabbix",
                "definition": "",
                "description": None,
                "error": None,
                "hide": 0,
                "includeAll": False,
                "label": "Group",
                "multi": False,
                "multiFormat": "glob",
                "name": "group",
                "options": [],
                "query": "*",
                "refresh": 1,
                "refresh_on_load": False,
                "regex": "",
                "skipUrlSync": False,
                "sort": 0,
                "tagValuesQuery": "",
                "tags": [],
                "tagsQuery": "",
                "type": "query",
                "useTags": False
            },
            {
                "allFormat": "glob",
                "allValue": None,
                "current": {
                    "selected": False,
                    "text": "kvm",
                    "value": "kvm"
                },
                "datasource": "Zabbix",
                "definition": "",
                "description": None,
                "error": None,
                "hide": 0,
                "includeAll": False,
                "label": "Host",
                "multi": False,
                "multiFormat": "glob",
                "name": "host",
                "options": [],
                "query": "$group.*",
                "refresh": 1,
                "refresh_on_load": False,
                "regex": "",
                "skipUrlSync": False,
                "sort": 0,
                "tagValuesQuery": "",
                "tags": [],
                "tagsQuery": "",
                "type": "query",
                "useTags": False
            },
            {
                "allFormat": "regex values",
                "allValue": None,
                "current": {
                    "selected": False,
                    "text": "All",
                    "value": "$__all"
                },
                "datasource": "Zabbix",
                "definition": "",
                "description": None,
                "error": None,
                "hide": 0,
                "hideLabel": False,
                "includeAll": True,
                "label": "Network interface",
                "multi": True,
                "multiFormat": "regex values",
                "name": "netif",
                "options": [],
                "query": "*.$host.Network interfaces.*",
                "refresh": 1,
                "refresh_on_load": False,
                "regex": "/(?:Incoming|Outgoing) network traffic on (.*)/",
                "skipUrlSync": False,
                "sort": 0,
                "tagValuesQuery": "",
                "tags": [],
                "tagsQuery": "",
                "type": "query",
                "useTags": False
            }
        ]
    },
    "time": {
        "from": "now-3h",
        "to": "now"
    },
    "timepicker": {
        "now": True,
        "refresh_intervals": [
            "30s",
            "1m",
            "5m",
            "15m",
            "30m",
            "1h",
            "3h",
            "2h",
            "1d"
        ],
        "time_options": [
            "5m",
            "15m",
            "1h",
            "6h",
            "12h",
            "24h",
            "2d",
            "7d",
            "30d"
        ]
    },
    "timezone": "browser",
    "title": "默认监控大屏",
    "version": 4
}


request_dict = {
    "dashboard": default_monitor_dashboard_dict,
    "folderId": 0,
    "overwrite": False
}
