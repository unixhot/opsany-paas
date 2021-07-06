default_host_dashboard_dict = {
    "annotations": {
      "list": [
        {
          "builtIn": 1,
          "datasource": "-- Grafana --",
          "enable": True,
          "hide": True,
          "iconColor": "rgba(0, 211, 255, 1)",
          "name": "Annotations & Alerts",
          "type": "dashboard"
        }
      ]
    },
    "editable": True,
    "gnetId": None,
    "graphTooltip": 0,
    "id": None,
    "iteration": 1625236780613,
    "links": [],
    "panels": [
      {
        "datasource": None,
        "gridPos": {
          "h": 1,
          "w": 24,
          "x": 0,
          "y": 0
        },
        "id": 27,
        "title": "System",
        "type": "row"
      },
      {
        "datasource": None,
        "description": "当前登录到系统的用户数",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 0,
          "y": 1
        },
        "id": 21,
        "options": {
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "showThresholdLabels": False,
          "showThresholdMarkers": True,
          "text": {}
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "General"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Number of logged in users"
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
          }
        ],
        "timeFrom": None,
        "timeShift": None,
        "title": "当前登录用户",
        "type": "gauge"
      },
      {
        "datasource": None,
        "description": "系统当前处于运行队列的进程数",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 3,
          "y": 1
        },
        "id": 23,
        "options": {
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "showThresholdLabels": False,
          "showThresholdMarkers": True,
          "text": {}
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "General"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Number of running processes"
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
          }
        ],
        "title": "运行中进程",
        "type": "gauge"
      },
      {
        "datasource": None,
        "description": "系统运行的进程总数",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 7,
          "x": 6,
          "y": 1
        },
        "id": 25,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "text": {},
          "textMode": "auto"
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "General"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Number of processes"
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
          }
        ],
        "title": "进程总数",
        "type": "stat"
      },
      {
        "cards": {
          "cardPadding": None,
          "cardRound": None
        },
        "color": {
          "cardColor": "#b4ff00",
          "colorScale": "sqrt",
          "colorScheme": "interpolateOranges",
          "exponent": 0.5,
          "mode": "spectrum"
        },
        "dataFormat": "timeseries",
        "datasource": None,
        "description": "Agent连接状态",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {
              "align": None,
              "filterable": False
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 11,
          "x": 13,
          "y": 1
        },
        "heatmap": {},
        "hideZeroBuckets": False,
        "highlightCards": True,
        "id": 19,
        "legend": {
          "show": False
        },
        "pluginVersion": "7.3.5",
        "reverseYBuckets": False,
        "targets": [
          {
            "application": {
              "filter": "Status"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Zabbix agent availability"
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
          }
        ],
        "title": "Agent可用性",
        "tooltip": {
          "show": True,
          "showHistogram": False
        },
        "type": "heatmap",
        "xAxis": {
          "show": True
        },
        "xBucketNumber": None,
        "xBucketSize": None,
        "yAxis": {
          "decimals": None,
          "format": "short",
          "logBase": 1,
          "max": None,
          "min": None,
          "show": True,
          "splitFactor": None
        },
        "yBucketBound": "auto",
        "yBucketNumber": None,
        "yBucketSize": None
      },
      {
        "collapsed": False,
        "datasource": None,
        "gridPos": {
          "h": 1,
          "w": 24,
          "x": 0,
          "y": 6
        },
        "id": 17,
        "panels": [],
        "title": "CPU",
        "type": "row"
      },
      {
        "datasource": None,
        "description": "主机的CPU总核数",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 0,
          "y": 7
        },
        "id": 9,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "text": {},
          "textMode": "auto"
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "CPU"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Number of CPUs"
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
          }
        ],
        "title": "CPU核数",
        "type": "stat"
      },
      {
        "aliasColors": {},
        "bars": False,
        "dashLength": 10,
        "dashes": False,
        "datasource": None,
        "description": "主机的5分钟平均负载",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "fill": 1,
        "fillGradient": 0,
        "gridPos": {
          "h": 5,
          "w": 10,
          "x": 3,
          "y": 7
        },
        "hiddenSeries": False,
        "id": 11,
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
        "targets": [
          {
            "application": {
              "filter": "CPU"
            },
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
          }
        ],
        "thresholds": [],
        "timeFrom": None,
        "timeRegions": [],
        "timeShift": None,
        "title": "系统负载",
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
        "yaxes": [
          {
            "format": "short",
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
        "NonePointMode": "connected",
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
          "h": 5,
          "w": 11,
          "x": 13,
          "y": 7
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
        "stack": True,
        "steppedLine": False,
        "targets": [
          {
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
          }
        ],
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
        "yaxes": [
          {
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
        "collapsed": False,
        "datasource": None,
        "gridPos": {
          "h": 1,
          "w": 24,
          "x": 0,
          "y": 12
        },
        "id": 4,
        "panels": [],
        "repeat": None,
        "title": "Memory",
        "type": "row"
      },
      {
        "datasource": None,
        "description": "系统的内存总量",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {
              "align": None,
              "filterable": False
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 3,
          "x": 0,
          "y": 13
        },
        "id": 13,
        "options": {
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "showThresholdLabels": False,
          "showThresholdMarkers": True,
          "text": {}
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "Memory"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Total memory"
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
          }
        ],
        "title": "内存总大小",
        "type": "gauge"
      },
      {
        "datasource": None,
        "description": "当前系统的可用内存",
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "custom": {},
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": None
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            }
          },
          "overrides": []
        },
        "gridPos": {
          "h": 5,
          "w": 10,
          "x": 3,
          "y": 13
        },
        "id": 15,
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "justifyMode": "auto",
          "orientation": "auto",
          "reduceOptions": {
            "calcs": [
              "lastNotNull"
            ],
            "fields": "",
            "values": False
          },
          "text": {},
          "textMode": "auto"
        },
        "pluginVersion": "7.3.5",
        "targets": [
          {
            "application": {
              "filter": "Memory"
            },
            "functions": [],
            "group": {
              "filter": "$group"
            },
            "host": {
              "filter": "$host"
            },
            "item": {
              "filter": "Available memory"
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
          }
        ],
        "timeFrom": None,
        "timeShift": None,
        "title": "当前可用内存",
        "type": "stat"
      },
      {
        "NonePointMode": "None",
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
          "h": 5,
          "w": 11,
          "x": 13,
          "y": 13
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
        "targets": [
          {
            "application": {
              "filter": "Memory"
            },
            "functions": [],
            "group": {
              "filter": "$group"
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
          }
        ],
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
        "yaxes": [
          {
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
      "list": [
        {
          "allFormat": "regex values",
          "allValue": None,
          "current": {
            "selected": False,
            "text": "$group",
            "value": "$group"
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
            "text": "$host",
            "value": "$host"
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
    "title": "默认主机大屏",
    "version": 0
}


request_dict = {
    "dashboard": default_host_dashboard_dict,
    "folderId": 0,
    "overwrite": False
}
