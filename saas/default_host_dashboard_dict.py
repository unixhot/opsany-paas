default_host_dashboard_dict = {
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": True,
        "hide": True,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations * Alerts",
        "target": {
          "limit": 100,
          "matchAny": False,
          "tags": [],
          "type": "dashboard"
        },
        "type": "dashboard"
      }
    ]
  },
  "editable": True,
  "fiscalYearStartMonth": 0,
  "gnetId": 5363,
  "graphTooltip": 1,
  "id": None,
  "iteration": 1713352495219,
  "links": [],
  "liveNow": False,
  "panels": [
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 38,
      "targets": [
        {
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "refId": "A"
        }
      ],
      "title": "Info",
      "type": "row"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-purple",
            "mode": "fixed"
          },
          "decimals": 0,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "N/A"
                }
              },
              "type": "special"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          },
          "unit": "bytes"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 4,
        "x": 0,
        "y": 1
      },
      "hideTimeOverride": True,
      "id": 27,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "Memory"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Total memory"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "timeFrom": "10y",
      "title": "Total memory",
      "type": "stat"
    },
    {
      "datasource": {},
      "description": "System uptime",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "fixed"
          },
          "decimals": 2,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "OFFLINE"
                }
              },
              "type": "special"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          },
          "unit": "dtdurations"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 16,
        "x": 4,
        "y": 1
      },
      "hideTimeOverride": True,
      "id": 2,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "last"
          ],
          "fields": "",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "Status"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/[U-u]ptime/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Uptime",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-purple",
            "mode": "fixed"
          },
          "decimals": 0,
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 4,
        "x": 20,
        "y": 1
      },
      "hideTimeOverride": True,
      "id": 84,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
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
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "CPU"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Number of CPUs"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "timeFrom": "10y",
      "title": "Total CPUs",
      "type": "stat"
    },
    {
      "datasource": {},
      "fieldConfig": {
        "defaults": {
          "mappings": [
            {
              "options": {
                "1": {
                  "text": "ONLINE"
                }
              },
              "type": "value"
            },
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "OFFLINE"
                }
              },
              "type": "special"
            }
          ],
          "noValue": "OFFLINE",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "red",
                "value": None
              },
              {
                "color": "green",
                "value": 1
              }
            ]
          },
          "unit": "none"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 4,
        "x": 0,
        "y": 4
      },
      "hideTimeOverride": True,
      "id": 3,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "/.*/"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Zabbix agent ping"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "timeFrom": "5m",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "fixed"
          },
          "mappings": [
            {
              "options": {
                "Null": {
                  "text": "'hostname'"
                }
              },
              "type": "value"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 16,
        "x": 4,
        "y": 4
      },
      "hideTimeOverride": False,
      "id": 70,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
        "justifyMode": "auto",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "/^Host name of Zabbix agent running$/",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "Monitoring agent"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "hide": False,
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Host name of Zabbix agent running"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "2",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "timeFrom": "10y",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              },
              {
                "color": "yellow",
                "value": 1
              }
            ]
          },
          "unit": "none"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 3,
        "w": 4,
        "x": 20,
        "y": 4
      },
      "hideTimeOverride": True,
      "id": 10,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "background",
        "graphMode": "none",
        "justifyMode": "center",
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "/^triggers count$/",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "/.*/"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Perda de Pacotes"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "acknowledged": 2,
            "count": True,
            "disableDataAlignment": False,
            "hostProxy": False,
            "hostsInMaintenance": False,
            "limit": 1001,
            "minSeverity": 0,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "sortProblems": "default",
            "useTimeRange": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "4",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "showProblems": "problems",
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2,
            "minSeverity": 0
          }
        }
      ],
      "timeFrom": "5y",
      "title": "Problems",
      "type": "stat"
    },
    {
      "collapsed": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 7
      },
      "id": 35,
      "panels": [],
      "targets": [
        {
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "refId": "A"
        }
      ],
      "title": "Stats",
      "type": "row"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "N/A"
                }
              },
              "type": "special"
            }
          ],
          "max": 100,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "rgba(50, 172, 45, 0.97)",
                "value": None
              },
              {
                "color": "rgba(237, 129, 40, 0.89)",
                "value": 50
              },
              {
                "color": "rgba(245, 54, 54, 0.9)",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 0,
        "y": 8
      },
      "id": 5,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "orientation": "horizontal",
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
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "Memory"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Memory utilization"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Memory Utilization",
      "type": "gauge"
    },
    {
      "aliasColors": {
        "CPU system time": "#e24d42",
        "CPU utilization": "red",
        "Espaco livre na particao C: % (pfree)": "#629E51",
        "Espaco livre na particao D: % (pfree)": "#E5AC0E",
        "Memory utilization": "blue",
        "Used memory %": "#6ed0e0",
        "Used memory in %": "#70dbed"
      },
      "bars": False,
      "dashLength": 10,
      "dashes": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "decimals": 0,
      "fieldConfig": {
        "defaults": {
          "unit": "percent"
        },
        "overrides": []
      },
      "fill": 5,
      "fillGradient": 0,
      "gridPos": {
        "h": 6,
        "w": 16,
        "x": 4,
        "y": 8
      },
      "hiddenSeries": False,
      "id": 9,
      "legend": {
        "alignAsTable": False,
        "avg": True,
        "current": False,
        "hideEmpty": False,
        "hideZero": False,
        "max": False,
        "min": False,
        "rightSide": False,
        "show": True,
        "total": False,
        "values": True
      },
      "lines": True,
      "linewidth": 2,
      "links": [],
      "NonePointMode": "None",
      "options": {
        "alertThreshold": True
      },
      "percentage": False,
      "pluginVersion": "9.0.2",
      "pointradius": 5,
      "points": False,
      "renderer": "flot",
      "seriesOverrides": [
        {
          "$$hashKey": "object:810",
          "alias": "/CPU utilization/",
          "dashLength": 5,
          "dashes": True,
          "fill": 0,
          "lines": True,
          "linewidth": 3,
          "NonePointMode": "None",
          "spaceLength": 2,
          "yaxis": 2,
          "zindex": 2
        },
        {
          "$$hashKey": "object:811",
          "alias": "Memory utilization",
          "fillGradient": 7,
          "NonePointMode": "None",
          "pointradius": 2
        }
      ],
      "spaceLength": 10,
      "stack": False,
      "steppedLine": False,
      "targets": [
        {
          "application": {
            "filter": "CPU"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "CPU utilization"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        },
        {
          "application": {
            "filter": "Memory"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "hide": False,
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Memory utilization"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "B",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "thresholds": [],
      "timeRegions": [],
      "title": "Memory / CPU",
      "tooltip": {
        "shared": True,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "mode": "time",
        "show": True,
        "values": []
      },
      "yaxes": [
        {
          "$$hashKey": "object:3277",
          "decimals": 0,
          "format": "percent",
          "label": "",
          "logBase": 1,
          "max": "100",
          "min": "0",
          "show": True
        },
        {
          "$$hashKey": "object:3278",
          "decimals": 0,
          "format": "percent",
          "label": "",
          "logBase": 1,
          "max": "100",
          "min": "0",
          "show": True
        }
      ],
      "yaxis": {
        "align": True
      }
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "N/A"
                }
              },
              "type": "special"
            }
          ],
          "max": 100,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "rgba(50, 172, 45, 0.97)",
                "value": None
              },
              {
                "color": "rgba(237, 129, 40, 0.89)",
                "value": 50
              },
              {
                "color": "rgba(245, 54, 54, 0.9)",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 20,
        "y": 8
      },
      "id": 4,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "orientation": "horizontal",
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
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "CPU"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "CPU utilization"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "B",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "CPU utilization",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "Amount of time the CPU has been waiting for I/O to complete.",
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [],
          "max": 20,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              },
              {
                "color": "#EAB839",
                "value": 5
              },
              {
                "color": "red",
                "value": 10
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 0,
        "y": 14
      },
      "id": 22,
      "links": [],
      "options": {
        "colorMode": "background",
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
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "CPU"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/CPU (iowait|DPC) time/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "CPU iowait time",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-purple",
            "mode": "fixed"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 4,
        "y": 14
      },
      "id": 52,
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
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "General"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Number of processes"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Number of processes",
      "type": "stat"
    },
    {
      "datasource": {},
      "description": "",
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [],
          "max": 100,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              },
              {
                "color": "#EAB839",
                "value": 80
              },
              {
                "color": "red",
                "value": 95
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 9,
        "x": 8,
        "y": 14
      },
      "hideTimeOverride": False,
      "id": 15,
      "links": [],
      "options": {
        "displayMode": "lcd",
        "minVizHeight": 10,
        "minVizWidth": 0,
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": False
        },
        "showUnfilled": True,
        "text": {}
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "/Filesystem./"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [
            {
              "$$hashKey": "object:388",
              "def": {
                "category": "Alias",
                "defaultParams": [
                  "/(.*)/",
                  "$1"
                ],
                "name": "replaceAlias",
                "params": [
                  {
                    "name": "regexp",
                    "type": "string"
                  },
                  {
                    "name": "newAlias",
                    "type": "string"
                  }
                ]
              },
              "params": [
                "/: Space utilization/",
                "$'"
              ],
              "text": "replaceAlias(/: Space utilization/, $')"
            }
          ],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Space utilization/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Filesystem (Space utilization %)",
      "transformations": [],
      "type": "bargauge"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "The amount of disk devices in the system",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "fixed"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 3,
        "x": 17,
        "y": 14
      },
      "id": 94,
      "options": {
        "colorMode": "value",
        "graphMode": "none",
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
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "/Disk /"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Disk utilization/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Disk drives ",
      "transformations": [
        {
          "id": "calculateField",
          "options": {
            "mode": "reduceRow",
            "reduce": {
              "reducer": "count"
            },
            "replaceFields": True
          }
        }
      ],
      "type": "stat"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "Number of users who are currently logged in",
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-purple",
            "mode": "fixed"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": None
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 20,
        "y": 14
      },
      "id": 95,
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
      "pluginVersion": "9.0.2",
      "targets": [
        {
          "application": {
            "filter": "General"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "Number of logged in users"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Logged in Users",
      "type": "stat"
    },
    {
      "collapsed": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 20
      },
      "id": 31,
      "panels": [],
      "targets": [
        {
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "refId": "A"
        }
      ],
      "title": "Disks",
      "type": "row"
    },
    {
      "aliasColors": {
        "CPU system time": "#e24d42",
        "CPU utilization": "red",
        "Espaco livre na particao C: % (pfree)": "#629E51",
        "Espaco livre na particao D: % (pfree)": "#E5AC0E",
        "Memory utilization": "blue",
        "Used memory %": "#6ed0e0",
        "Used memory in %": "#70dbed"
      },
      "bars": False,
      "dashLength": 10,
      "dashes": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "decimals": 0,
      "fieldConfig": {
        "defaults": {
          "unit": "ops"
        },
        "overrides": []
      },
      "fill": 10,
      "fillGradient": 6,
      "gridPos": {
        "h": 6,
        "w": 10,
        "x": 0,
        "y": 21
      },
      "hiddenSeries": False,
      "id": 89,
      "legend": {
        "alignAsTable": False,
        "avg": True,
        "current": False,
        "hideEmpty": False,
        "hideZero": False,
        "max": False,
        "min": False,
        "rightSide": False,
        "show": True,
        "total": False,
        "values": True
      },
      "lines": True,
      "linewidth": 2,
      "links": [],
      "NonePointMode": "connected",
      "options": {
        "alertThreshold": True
      },
      "percentage": False,
      "pluginVersion": "9.0.2",
      "pointradius": 5,
      "points": False,
      "renderer": "flot",
      "repeat": "Disk",
      "repeatDirection": "v",
      "seriesOverrides": [
        {
          "$$hashKey": "object:810",
          "alias": "/read rate/",
          "color": "#5794F2",
          "fill": 0,
          "lines": True,
          "linewidth": 3
        },
        {
          "$$hashKey": "object:811",
          "alias": "/write rate/",
          "color": "#C4162A",
          "pointradius": 2,
          "points": True
        }
      ],
      "spaceLength": 10,
      "stack": False,
      "steppedLine": False,
      "targets": [
        {
          "application": {
            "filter": "$Disk"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/write rate/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        },
        {
          "application": {
            "filter": "$Disk"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "hide": False,
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/read rate/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "B",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "thresholds": [],
      "timeRegions": [],
      "title": "$Disk (read/write rates)",
      "tooltip": {
        "shared": True,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "mode": "time",
        "show": True,
        "values": []
      },
      "yaxes": [
        {
          "$$hashKey": "object:3277",
          "decimals": 0,
          "format": "ops",
          "label": "",
          "logBase": 1,
          "min": "0",
          "show": True
        },
        {
          "$$hashKey": "object:3278",
          "decimals": 0,
          "format": "none",
          "label": "",
          "logBase": 1,
          "min": "0",
          "show": False
        }
      ],
      "yaxis": {
        "align": False
      }
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "This item is the percentage of elapsed time that the selected disk drive was busy servicing read or writes requests.",
      "fieldConfig": {
        "defaults": {
          "decimals": 0,
          "mappings": [],
          "max": 100,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "#EAB839",
                "value": 50
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 6,
        "w": 4,
        "x": 10,
        "y": 21
      },
      "id": 23,
      "links": [],
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
      "pluginVersion": "9.0.2",
      "repeat": "Disk",
      "repeatDirection": "v",
      "targets": [
        {
          "application": {
            "filter": "$Disk"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [
            {
              "$$hashKey": "object:976",
              "def": {
                "category": "Alias",
                "defaultParams": [
                  "/(.*)/",
                  "$1"
                ],
                "name": "replaceAlias",
                "params": [
                  {
                    "name": "regexp",
                    "type": "string"
                  },
                  {
                    "name": "newAlias",
                    "type": "string"
                  }
                ]
              },
              "params": [
                "/(: Disk utilization)/",
                "$'"
              ],
              "text": "replaceAlias(/(: Disk utilization)/, $')"
            }
          ],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Disk utilization/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "$Disk (Performance)",
      "type": "gauge"
    },
    {
      "aliasColors": {
        "C:: Total space": "rgb(255, 255, 255)",
        "C:: Used space": "red",
        "CPU system time": "#e24d42",
        "Espaco livre na particao C: % (pfree)": "#629E51",
        "Espaco livre na particao D: % (pfree)": "#E5AC0E",
        "Used memory %": "#6ed0e0"
      },
      "bars": False,
      "dashLength": 10,
      "dashes": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "decimals": 0,
      "description": "Used storage in Bytes",
      "fieldConfig": {
        "defaults": {
          "unit": "bytes"
        },
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 4,
      "gridPos": {
        "h": 6,
        "w": 10,
        "x": 14,
        "y": 21
      },
      "hiddenSeries": False,
      "id": 32,
      "legend": {
        "alignAsTable": False,
        "avg": False,
        "current": True,
        "hideEmpty": False,
        "hideZero": False,
        "max": False,
        "min": False,
        "rightSide": False,
        "show": True,
        "total": False,
        "values": True
      },
      "lines": True,
      "linewidth": 2,
      "links": [],
      "NonePointMode": "connected",
      "options": {
        "alertThreshold": True
      },
      "percentage": True,
      "pluginVersion": "9.0.2",
      "pointradius": 5,
      "points": False,
      "renderer": "flot",
      "repeat": "Filesystem",
      "repeatDirection": "v",
      "seriesOverrides": [
        {
          "$$hashKey": "object:1193",
          "alias": "/Used space/",
          "color": "#F2495C",
          "dashLength": 7,
          "dashes": True,
          "fill": 10,
          "fillGradient": 10,
          "linewidth": 4,
          "spaceLength": 4
        },
        {
          "$$hashKey": "object:3296",
          "alias": "/Total space/",
          "color": "rgb(255, 255, 255)",
          "linewidth": 4
        }
      ],
      "spaceLength": 10,
      "stack": False,
      "steppedLine": False,
      "targets": [
        {
          "application": {
            "filter": "$Filesystem"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "hide": False,
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/(Used|Total) space/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "thresholds": [],
      "timeRegions": [],
      "title": "$Filesystem (Space utilization)",
      "tooltip": {
        "shared": True,
        "sort": 2,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "mode": "time",
        "show": True,
        "values": []
      },
      "yaxes": [
        {
          "$$hashKey": "object:1664",
          "decimals": 0,
          "format": "bytes",
          "label": "",
          "logBase": 1,
          "min": "0",
          "show": True
        },
        {
          "$$hashKey": "object:1665",
          "decimals": 0,
          "format": "bytes",
          "label": "",
          "logBase": 1,
          "show": False
        }
      ],
      "yaxis": {
        "align": True
      }
    },
    {
      "collapsed": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 27
      },
      "id": 41,
      "panels": [],
      "targets": [
        {
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "refId": "A"
        }
      ],
      "title": "Network",
      "type": "row"
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "description": "",
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "semi-dark-green",
            "mode": "fixed"
          },
          "decimals": 0,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "N/A"
                }
              },
              "type": "special"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              }
            ]
          },
          "unit": "binBps"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 7,
        "w": 4,
        "x": 0,
        "y": 28
      },
      "id": 19,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "repeat": "Network",
      "repeatDirection": "v",
      "targets": [
        {
          "application": {
            "filter": "$Network"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Bits received/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "(IN) $Network",
      "type": "stat"
    },
    {
      "aliasColors": {
        "Incoming network traffic on vmxnet3 Ethernet Adapter #2": "#1f78c1",
        "Outgoing network traffic on vmxnet3 Ethernet Adapter #2": "rgba(237, 129, 40, 0.79)",
        "Outgoing network traffic on vmxnet3 Ethernet Adapter #2-WFP LightWeight Filter-0000": "rgba(237, 129, 40, 0.89)"
      },
      "bars": False,
      "dashLength": 10,
      "dashes": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "decimals": 0,
      "fieldConfig": {
        "defaults": {
          "unit": "binBps"
        },
        "overrides": []
      },
      "fill": 5,
      "fillGradient": 3,
      "gridPos": {
        "h": 7,
        "w": 16,
        "x": 4,
        "y": 28
      },
      "hiddenSeries": False,
      "id": 18,
      "legend": {
        "alignAsTable": True,
        "avg": False,
        "current": True,
        "hideEmpty": True,
        "hideZero": True,
        "max": False,
        "min": False,
        "rightSide": True,
        "show": False,
        "total": False,
        "values": True
      },
      "lines": True,
      "linewidth": 3,
      "links": [],
      "NonePointMode": "connected",
      "options": {
        "alertThreshold": True
      },
      "percentage": False,
      "pluginVersion": "9.0.2",
      "pointradius": 5,
      "points": False,
      "renderer": "flot",
      "repeat": "Network",
      "repeatDirection": "v",
      "seriesOverrides": [
        {
          "$$hashKey": "object:3135",
          "alias": "/Bits received/",
          "color": "#56A64B"
        },
        {
          "$$hashKey": "object:3136",
          "alias": "/Bits sent/",
          "color": "#8F3BB8",
          "transform": "negative-Y"
        }
      ],
      "spaceLength": 10,
      "stack": False,
      "steppedLine": False,
      "targets": [
        {
          "application": {
            "filter": "$netif"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [
            {
              "$$hashKey": "object:2368",
              "def": {
                "category": "Alias",
                "defaultParams": [
                  "/(.*)/",
                  "$1"
                ],
                "name": "replaceAlias",
                "params": [
                  {
                    "name": "regexp",
                    "type": "string"
                  },
                  {
                    "name": "newAlias",
                    "type": "string"
                  }
                ]
              },
              "params": [
                "/Interface /",
                "$`"
              ],
              "text": "replaceAlias(/Interface /, $`)"
            }
          ],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Bits (received|sent)/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "thresholds": [],
      "timeRegions": [],
      "title": "$Network",
      "tooltip": {
        "shared": True,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "mode": "time",
        "show": True,
        "values": []
      },
      "yaxes": [
        {
          "$$hashKey": "object:1888",
          "format": "bps",
          "logBase": 1,
          "show": True
        },
        {
          "$$hashKey": "object:1889",
          "format": "binBps",
          "logBase": 1,
          "show": True
        }
      ],
      "yaxis": {
        "align": False
      }
    },
    {
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "semi-dark-purple",
            "mode": "fixed"
          },
          "decimals": 0,
          "mappings": [
            {
              "options": {
                "match": "None",
                "result": {
                  "text": "N/A"
                }
              },
              "type": "special"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              }
            ]
          },
          "unit": "binBps"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 7,
        "w": 4,
        "x": 20,
        "y": 28
      },
      "id": 21,
      "links": [],
      "maxDataPoints": 100,
      "options": {
        "colorMode": "value",
        "graphMode": "area",
        "justifyMode": "auto",
        "orientation": "horizontal",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": False
        },
        "text": {},
        "textMode": "value"
      },
      "pluginVersion": "9.0.2",
      "repeat": "Network",
      "repeatDirection": "v",
      "targets": [
        {
          "application": {
            "filter": "$Network"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": "/Bits sent/"
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "count": True,
            "disableDataAlignment": False,
            "minSeverity": 3,
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "0",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "(OUT) $Network",
      "type": "stat"
    },
    {
      "collapsed": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "gridPos": {
        "h": 1,
        "w": 24,
        "x": 0,
        "y": 35
      },
      "id": 29,
      "panels": [],
      "targets": [
        {
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "refId": "A"
        }
      ],
      "title": "Problems",
      "type": "row"
    },
    {
      "ackEventColor": "rgb(56, 219, 156)",
      "ackField": True,
      "ageField": True,
      "customLastChangeFormat": False,
      "datasource": {
        "type": "alexanderzobnin-zabbix-datasource",
        "uid": "${DATA_SOURCE}"
      },
      "descriptionAtNewLine": False,
      "descriptionField": True,
      "fontSize": "120%",
      "gridPos": {
        "h": 12,
        "w": 24,
        "x": 0,
        "y": 36
      },
      "highlightBackground": True,
      "highlightNewEvents": True,
      "highlightNewerThan": "1h",
      "hostField": False,
      "hostGroups": False,
      "hostProxy": False,
      "hostTechNameField": False,
      "id": 17,
      "lastChangeFormat": "",
      "layout": "table",
      "limit": 100,
      "links": [],
      "markAckEvents": True,
      "okEventColor": "rgb(56, 189, 113)",
      "options": {
        "ackEventColor": "rgb(56, 219, 156)",
        "ackField": True,
        "ageField": True,
        "allowDangerousHTML": False,
        "customLastChangeFormat": False,
        "descriptionAtNewLine": False,
        "descriptionField": True,
        "fontSize": "120%",
        "highlightBackground": True,
        "highlightNewEvents": True,
        "highlightNewerThan": "1h",
        "hostField": False,
        "hostGroups": False,
        "hostProxy": False,
        "hostTechNameField": False,
        "lastChangeFormat": "",
        "layout": "table",
        "limit": 100,
        "markAckEvents": True,
        "okEventColor": "rgb(56, 189, 113)",
        "opdataField": False,
        "pageSize": 10,
        "problemTimeline": True,
        "resizedColumns": [
          {
            "id": "lastchange",
            "value": 187
          },
          {
            "id": "age",
            "value": 125
          },
          {
            "id": "ack",
            "value": 207
          },
          {
            "id": "description",
            "value": 899
          }
        ],
        "severityField": True,
        "showTags": False,
        "sortProblems": "lastchange",
        "statusField": False,
        "statusIcon": True,
        "triggerSeverity": [
          {
            "$$hashKey": "object:738",
            "color": "rgb(108, 108, 108)",
            "priority": 0,
            "severity": "Not classified",
            "show": True
          },
          {
            "$$hashKey": "object:739",
            "color": "rgb(120, 158, 183)",
            "priority": 1,
            "severity": "Information",
            "show": True
          },
          {
            "$$hashKey": "object:740",
            "color": "rgb(175, 180, 36)",
            "priority": 2,
            "severity": "Warning",
            "show": True
          },
          {
            "$$hashKey": "object:741",
            "color": "rgb(255, 137, 30)",
            "priority": 3,
            "severity": "Average",
            "show": True
          },
          {
            "$$hashKey": "object:742",
            "color": "rgb(255, 101, 72)",
            "priority": 4,
            "severity": "High",
            "show": True
          },
          {
            "$$hashKey": "object:743",
            "color": "rgb(215, 0, 0)",
            "priority": 5,
            "severity": "Disaster",
            "show": True
          }
        ]
      },
      "pageSize": 10,
      "pluginVersion": "9.0.2",
      "problemTimeline": True,
      "resizedColumns": [
        {
          "id": "lastchange",
          "value": 187
        },
        {
          "id": "age",
          "value": 125
        },
        {
          "id": "ack",
          "value": 207
        },
        {
          "id": "description",
          "value": 899
        }
      ],
      "schemaVersion": 8,
      "severityField": True,
      "showTags": False,
      "sortProblems": "lastchange",
      "statusField": False,
      "statusIcon": True,
      "targets": [
        {
          "application": {
            "filter": "/.*/"
          },
          "countTriggersBy": "",
          "datasource": {
            "type": "alexanderzobnin-zabbix-datasource",
            "uid": "${DATA_SOURCE}"
          },
          "functions": [],
          "group": {
            "filter": "$Group"
          },
          "host": {
            "filter": "$Host"
          },
          "item": {
            "filter": ""
          },
          "itemTag": {
            "filter": ""
          },
          "macro": {
            "filter": ""
          },
          "options": {
            "acknowledged": 2,
            "count": True,
            "disableDataAlignment": False,
            "hostProxy": False,
            "hostsInMaintenance": False,
            "limit": 1001,
            "minSeverity": 3,
            "severities": [
              0,
              1,
              2,
              3,
              4,
              5
            ],
            "showDisabledItems": False,
            "skipEmptyValues": False,
            "sortProblems": "default",
            "useTimeRange": False,
            "useTrends": "default",
            "useZabbixValueMapping": False
          },
          "proxy": {
            "filter": ""
          },
          "queryType": "5",
          "refId": "A",
          "resultFormat": "time_series",
          "schema": 12,
          "showProblems": "problems",
          "table": {
            "skipEmptyValues": False
          },
          "tags": {
            "filter": ""
          },
          "textFilter": "",
          "trigger": {
            "filter": ""
          },
          "triggers": {
            "acknowledged": 2
          }
        }
      ],
      "title": "Problems",
      "triggerSeverity": [
        {
          "$$hashKey": "object:738",
          "color": "rgb(108, 108, 108)",
          "priority": 0,
          "severity": "Not classified",
          "show": True
        },
        {
          "$$hashKey": "object:739",
          "color": "rgb(120, 158, 183)",
          "priority": 1,
          "severity": "Information",
          "show": True
        },
        {
          "$$hashKey": "object:740",
          "color": "rgb(175, 180, 36)",
          "priority": 2,
          "severity": "Warning",
          "show": True
        },
        {
          "$$hashKey": "object:741",
          "color": "rgb(255, 137, 30)",
          "priority": 3,
          "severity": "Average",
          "show": True
        },
        {
          "$$hashKey": "object:742",
          "color": "rgb(255, 101, 72)",
          "priority": 4,
          "severity": "High",
          "show": True
        },
        {
          "$$hashKey": "object:743",
          "color": "rgb(215, 0, 0)",
          "priority": 5,
          "severity": "Disaster",
          "show": True
        }
      ],
      "type": "alexanderzobnin-zabbix-triggers-panel"
    }
  ],
  "refresh": "30s",
  "schemaVersion": 36,
  "style": "dark",
  "tags": [
    "zabbix"
  ],
  "templating": {
    "list": [
      {
        "current": {
          "selected": False,
          "text": "Zabbix",
          "value": "Zabbix"
        },
        "description": "请选择Zabbix监控实例",
        "hide": 0,
        "includeAll": False,
        "label": "监控实例:",
        "multi": False,
        "name": "DATA_SOURCE",
        "options": [],
        "query": "alexanderzobnin-zabbix-datasource",
        "queryValue": "",
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "type": "datasource"
      },
      {
        "allFormat": "regex values",
        "current": {
          "selected": False,
          "text": "默认分组",
          "value": "默认分组"
        },
        "datasource": {
          "type": "alexanderzobnin-zabbix-datasource",
          "uid": "${DATA_SOURCE}"
        },
        "definition": "Zabbix - group",
        "hide": 0,
        "includeAll": False,
        "label": "分组:",
        "multi": False,
        "multiFormat": "glob",
        "name": "Group",
        "options": [],
        "query": {
          "application": "",
          "group": "/.*/",
          "host": "",
          "item": "",
          "itemTag": "",
          "queryType": "group"
        },
        "refresh": 1,
        "refresh_on_load": False,
        "regex": "",
        "skipUrlSync": False,
        "sort": 0,
        "tagValuesQuery": "",
        "tagsQuery": "",
        "type": "query",
        "useTags": False
      },
      {
        "current": {
          "selected": False,
          "text": "Ubuntu20.04",
          "value": "Ubuntu20.04"
        },
        "datasource": {
          "type": "alexanderzobnin-zabbix-datasource",
          "uid": "${DATA_SOURCE}"
        },
        "definition": "Zabbix - host",
        "hide": 0,
        "includeAll": False,
        "label": "名称:",
        "multi": False,
        "name": "Host",
        "options": [],
        "query": {
          "application": "",
          "group": "$Group",
          "host": "/.*/",
          "item": "",
          "itemTag": "",
          "queryType": "host"
        },
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "sort": 0,
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-30m",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
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
  "title": "主机大屏",
  "description": "Zabbix主机大屏",
  "uid": "opsany-zabbix-host-dashboard",
  "version": 25,
  "weekStart": ""
}

