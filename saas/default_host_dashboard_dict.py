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
    "description": "Nice and clean status about your server.",
    "editable": True,
    "gnetId": None,
    "graphTooltip": 0,
    "id": None,
    "iteration": 1623529989121,
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
            "id": 38,
            "title": "Info",
            "type": "row"
        },
        {
            
            "datasource": None,
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "fixedColor": "dark-purple",
                        "mode": "fixed"
                    },
                    "decimals": 0,
                    "mappings": [
                        {
                            "id": 0,
                            "op": "=",
                            "text": "N/A",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
                    "fields": "/^Total memory$/",
                    "values": False
                },
                "text": {},
                "textMode": "value"
            },
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "Memory"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "title": "Total memory",
            "type": "stat"
        },
        {
            "cacheTimeout": None,
            "datasource": None,
            "description": "System uptime",
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "fixed"
                    },
                    "decimals": 2,
                    "mappings": [
                        {
                            "id": 0,
                            "op": "=",
                            "text": "OFFLINE",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "Status"
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
                    "options": {
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
            "title": "Uptime",
            "type": "stat"
        },
        {
            "datasource": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "CPU"
                    },
                    "functions": [],
                    "group": {
                        "filter": "$Group"
                    },
                    "host": {
                        "filter": "$Host"
                    },
                    "item": {
                        "filter": "/Number of (CPUs|cores)/"
                    },
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "timeFrom": "10y",
            "timeShift": None,
            "title": "Total CPUs",
            "type": "stat"
        },
        {
            "cacheTimeout": None,
            "datasource": None,
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "from": "1",
                            "id": 0,
                            "op": "=",
                            "text": "ONLINE",
                            "to": "100",
                            "type": 1,
                            "value": "1"
                        },
                        {
                            "id": 1,
                            "op": "=",
                            "text": "OFFLINE",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "/.*/"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "timeFrom": "5m",
            "timeShift": None,
            "type": "stat"
        },
        {
            "datasource": None,
            "description": "",
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "mode": "fixed"
                    },
                    "mappings": [
                        {
                            "from": "",
                            "id": 2,
                            "text": "'hostname'",
                            "to": "",
                            "type": 1,
                            "value": "Null"
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "Monitoring agent"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 2,
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
            "timeFrom": "10y",
            "timeShift": None,
            "type": "stat"
        },
        {
            "cacheTimeout": None,
            "datasource": None,
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "/.*/"
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
                    "options": {
                        "showDisabledItems": False,
                        "skipEmptyValues": False
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 4,
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
            "datasource": None,
            "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 7
            },
            "id": 35,
            "panels": [],
            "title": "Stats",
            "type": "row"
        },
        {
            "cacheTimeout": None,
            "datasource": None,
            "fieldConfig": {
                "defaults": {
                    "decimals": 0,
                    "mappings": [
                        {
                            "id": 0,
                            "op": "=",
                            "text": "N/A",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "Memory"
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
                    "options": {
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
            "title": "Memory Utilization",
            "type": "gauge"
        },
        {
            "aliasColors": {
                "CPU system time": "#e24d42",
                "CPU utilization": "red",
                "Espaço livre na partição C: % (pfree)": "#629E51",
                "Espaço livre na partição D: % (pfree)": "#E5AC0E",
                "Memory utilization": "blue",
                "Used memory %": "#6ed0e0",
                "Used memory in %": "#70dbed"
            },
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": None,
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
            "pluginVersion": "7.5.7",
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
                    "options": {
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
                },
                {
                    "application": {
                        "filter": "Memory"
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
                    "options": {
                        "showDisabledItems": False,
                        "skipEmptyValues": False
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 0,
                    "refId": "B",
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
            "title": "Memory / CPU",
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
                "align": True,
                "alignLevel": None
            }
        },
        {
            "cacheTimeout": None,
            "datasource": None,
            "fieldConfig": {
                "defaults": {
                    "decimals": 0,
                    "mappings": [
                        {
                            "id": 0,
                            "op": "=",
                            "text": "N/A",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "CPU"
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
                    "options": {
                        "showDisabledItems": False,
                        "skipEmptyValues": False
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 0,
                    "refId": "B",
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
            "title": "CPU utilization",
            "type": "gauge"
        },
        {
            "datasource": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "CPU"
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
                    "options": {
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
            "title": "CPU iowait time",
            "type": "stat"
        },
        {
            "datasource": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "General"
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
                    "options": {
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
            "title": "Number of processes",
            "type": "stat"
        },
        {
            "datasource": None,
            "description": "",
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "/Filesystem./"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "title": "Filesystem (Space utilization %)",
            "transformations": [],
            "type": "bargauge"
        },
        {
            "datasource": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "/Disk /"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "datasource": None,
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
            "pluginVersion": "7.5.7",
            "targets": [
                {
                    "application": {
                        "filter": "General"
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "title": "Logged in Users",
            "type": "stat"
        },
        {
            "collapsed": False,
            "datasource": None,
            "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 20
            },
            "id": 31,
            "panels": [],
            "title": "Disks",
            "type": "row"
        },
        {
            "aliasColors": {
                "CPU system time": "#e24d42",
                "CPU utilization": "red",
                "Espaço livre na partição C: % (pfree)": "#629E51",
                "Espaço livre na partição D: % (pfree)": "#E5AC0E",
                "Memory utilization": "blue",
                "Used memory %": "#6ed0e0",
                "Used memory in %": "#70dbed"
            },
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": None,
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
            "pluginVersion": "7.5.7",
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
                    "options": {
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
                },
                {
                    "application": {
                        "filter": "$Disk"
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
                    "options": {
                        "showDisabledItems": False,
                        "skipEmptyValues": False
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 0,
                    "refId": "B",
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
            "title": "$Disk (read/write rates)",
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
                    "$$hashKey": "object:3277",
                    "decimals": 0,
                    "format": "ops",
                    "label": "",
                    "logBase": 1,
                    "max": None,
                    "min": "0",
                    "show": True
                },
                {
                    "$$hashKey": "object:3278",
                    "decimals": 0,
                    "format": "none",
                    "label": "",
                    "logBase": 1,
                    "max": None,
                    "min": "0",
                    "show": False
                }
            ],
            "yaxis": {
                "align": False,
                "alignLevel": None
            }
        },
        {
            "datasource": None,
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
                                "color": "green",
                                "value": None
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
            "pluginVersion": "7.5.7",
            "repeat": "Disk",
            "repeatDirection": "v",
            "targets": [
                {
                    "application": {
                        "filter": "$Disk"
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
                    "options": {
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
            "title": "$Disk (Performance)",
            "type": "gauge"
        },
        {
            "aliasColors": {
                "C:: Total space": "rgb(255, 255, 255)",
                "C:: Used space": "red",
                "CPU system time": "#e24d42",
                "Espaço livre na partição C: % (pfree)": "#629E51",
                "Espaço livre na partição D: % (pfree)": "#E5AC0E",
                "Used memory %": "#6ed0e0"
            },
            "bars": False,
            "dashLength": 10,
            "dashes": False,
            "datasource": None,
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
            "pluginVersion": "7.5.7",
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
                    "options": {
                        "disableDataAlignment": False,
                        "showDisabledItems": False,
                        "skipEmptyValues": False,
                        "useZabbixValueMapping": False
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
            "title": "$Filesystem (Space utilization)",
            "tooltip": {
                "shared": True,
                "sort": 2,
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
                    "$$hashKey": "object:1664",
                    "decimals": 0,
                    "format": "bytes",
                    "label": "",
                    "logBase": 1,
                    "max": None,
                    "min": "0",
                    "show": True
                },
                {
                    "$$hashKey": "object:1665",
                    "decimals": 0,
                    "format": "bytes",
                    "label": "",
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": False
                }
            ],
            "yaxis": {
                "align": True,
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
                "y": 27
            },
            "id": 41,
            "panels": [],
            "title": "Network",
            "type": "row"
        },
        {
            "cacheTimeout": None,
            "datasource": None,
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
                            "id": 0,
                            "op": "=",
                            "text": "N/A",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "repeat": "Network",
            "repeatDirection": "v",
            "targets": [
                {
                    "application": {
                        "filter": "$Network"
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
                    "options": {
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
            "datasource": None,
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
                "sideWidth": None,
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
            "pluginVersion": "7.5.7",
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
                        "filter": "$Network"
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
                    "options": {
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
            "title": "$Network",
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
                    "$$hashKey": "object:1888",
                    "decimals": None,
                    "format": "bps",
                    "label": None,
                    "logBase": 1,
                    "max": None,
                    "min": None,
                    "show": True
                },
                {
                    "$$hashKey": "object:1889",
                    "format": "binBps",
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
            "cacheTimeout": None,
            "datasource": None,
            "fieldConfig": {
                "defaults": {
                    "color": {
                        "fixedColor": "semi-dark-purple",
                        "mode": "fixed"
                    },
                    "decimals": 0,
                    "mappings": [
                        {
                            "id": 0,
                            "op": "=",
                            "text": "N/A",
                            "type": 1,
                            "value": "None"
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
            "interval": None,
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
            "pluginVersion": "7.5.7",
            "repeat": "Network",
            "repeatDirection": "v",
            "targets": [
                {
                    "application": {
                        "filter": "$Network"
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
                    "options": {
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
            "title": "(OUT) $Network",
            "type": "stat"
        },
        {
            "collapsed": False,
            "datasource": None,
            "gridPos": {
                "h": 1,
                "w": 24,
                "x": 0,
                "y": 35
            },
            "id": 29,
            "panels": [],
            "title": "Problems",
            "type": "row"
        },
        {
            "ackEventColor": "rgb(56, 219, 156)",
            "ackField": True,
            "ageField": True,
            "customLastChangeFormat": False,
            "datasource": None,
            "descriptionAtNewLine": False,
            "descriptionField": True,
            "fieldConfig": {
                "defaults": {},
                "overrides": []
            },
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
                    "options": {
                        "acknowledged": 2,
                        "hostProxy": False,
                        "hostsInMaintenance": False,
                        "limit": 1001,
                        "minSeverity": 0,
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
                        "sortProblems": "default"
                    },
                    "proxy": {
                        "filter": ""
                    },
                    "queryType": 5,
                    "refId": "A",
                    "resultFormat": "time_series",
                    "showProblems": "problems",
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
    "schemaVersion": 27,
    "style": "dark",
    "tags": [
        "zabbix"
    ],
    "templating": {
        "list": [
            {
                "allFormat": "regex values",
                "allValue": None,
                "current": {
                    "selected": False,
                    "text": "$Group",
                    "value": "$Group"
                },
                "datasource": None,
                "definition": "",
                "description": None,
                "error": None,
                "hide": 0,
                "includeAll": False,
                "label": "Group",
                "multi": False,
                "multiFormat": "glob",
                "name": "Group",
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
                    "text": "$Host",
                    "value": "$Host"
                },
                "datasource": None,
                "definition": "",
                "description": None,
                "error": None,
                "hide": 0,
                "includeAll": False,
                "label": "Host",
                "multi": False,
                "multiFormat": "glob",
                "name": "Host",
                "options": [],
                "query": "$Group.*",
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
                "datasource": None,
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
        "from": "now-6h",
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
    "timezone": "",
    "title": "内置主机大屏",
    "uid": "built_in_host_dashboard",
    "version": 2
}

request_dict = {
    "dashboard": default_host_dashboard_dict,
    "folderId": 0,
    "overwrite": False
}
