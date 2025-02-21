# pingback_service
小程序/APP规则 与 PC/WAP规则区别：
1.两者取值字段有差异，对结果汇总对比无影响。
2.小程序/APP ev中d码确定为数字，所以会做是否连续校验，结果中排序也更为准确；PC/WAP则有可能为字符串，无法判断连续，排序为字符串排序规则。
3.小程序/APP中，如果一次测试内无PV及EV认为严重异常，不会生成汇总结果；PC/WAP则仅无PV认为严重异常，不会生成汇总结果。
4.小程序/APP中，不允许spmcnt为空情况下生成基础规则；PC/WAP则允许spmcnt为空情况下生成基础规则。
5.小程序/APP中，推荐策略固定，会进行具体值比较；PC/WAP则在scm以1开头时，仅对比有scm或无scm，非1开头时对比值是否一致
小程序/APP规则，某场景埋点规则查看样例：
{
    "full_rules": {
        "pv_rules": {
            "smwx-shw.home.0->smwx-shw.mySpace.0": 3,
            "smwx-shw.home.0->smwx-shw.mySpace.0-scm_pre": "",
            "smwx-shw.mySpace.0->smwx-shw.home.0": 2,
            "smwx-shw.mySpace.0->smwx-shw.home.0-scm_pre": "",
            "empty->smwx-shw.home.0": 1,
            "empty->smwx-shw.home.0-scm_pre": ""
        },
        "ev_rules": {
            "smwx-shw.mySpace.0->smwx-shw.home.feed-scm_cnt": "",
            "smwx-shw.mySpace.0->smwx-shw.home.feed": {
                "1": [
                    1,
                    2,
                    3,
                    4,
                    5,
                    6
                ],
                "1_is__series": true
            },
            "smwx-shw.home.0->smwx-shw.mySpace.all-scm_cnt": "",
            "smwx-shw.home.0->smwx-shw.mySpace.all": {
                "1": [
                    1,
                    2,
                    3
                ],
                "1_is__series": true
            }
        },
        "action_rules": {
            "smwx-shw.home.feed->10216": 3,
            "smwx-shw.home.feed->9910": 3,
            "smwx-shw.home.0->8725": 3,
            "smwx-shw.home.feed->9315": 3,
            "smwx-shw.mySpace.0->8983": 3,
            "smwx-shw.mySpace.0->8725": 3,
            "smwx-shw.home.feed->7202": 1
        }
    },
    "conclusion": {
        "pv_rules": [
            "由 smwx-shw.home.0 到 smwx-shw.mySpace.0 的PV，上报：3次",
            "由 smwx-shw.mySpace.0 到 smwx-shw.home.0 的PV，上报：2次",
            "由 empty 到 smwx-shw.home.0 的PV，上报：1次"
        ],
        "ev_rules": [
            "smwx-shw.home.feed 曝光 6 条数据，他们由 smwx-shw.mySpace.0 转化而来，其中出现 1 次的d码有：[1, 2, 3, 4, 5, 6]，这些d码是连续的；这些数据曝光没有scm推荐值。",
            "smwx-shw.mySpace.all 曝光 3 条数据，他们由 smwx-shw.home.0 转化而来，其中出现 1 次的d码有：[1, 2, 3]，这些d码是连续的；这些数据曝光没有scm推荐值。"
        ],
        "action__rules": [
            "在 smwx-shw.home.feed 页面，上报点击事件：10216 ，共计3次",
            "在 smwx-shw.home.feed 页面，上报点击事件：9910 ，共计3次",
            "在 smwx-shw.home.0 页面，上报点击事件：8725 ，共计3次",
            "在 smwx-shw.home.feed 页面，上报点击事件：9315 ，共计3次",
            "在 smwx-shw.mySpace.0 页面，上报点击事件：8983 ，共计3次",
            "在 smwx-shw.mySpace.0 页面，上报点击事件：8725 ，共计3次",
            "在 smwx-shw.home.feed 页面，上报点击事件：7202 ，共计1次"
        ]
    }
}
PC/WAP规则，某场景埋点规则查看样例：
{
    "full_rules": {
        "pv_rules": {
            "empty->smwp.content.0": 1,
            "empty->smwp.content.0-scm_pre": "empty"
        },
        "ev_rules": {
            "empty->empty-scm_cnt": "empty",
            "empty->empty": {
                "27": [
                    "empty"
                ]
            },
            "empty->smwp.content.nav-scm_cnt": "empty",
            "empty->smwp.content.nav": {
                "1": [
                    "3",
                    "4",
                    "5"
                ],
                "2": [
                    "2"
                ]
            },
            "empty->smwp.content.fd-d-scm_cnt": "9010.8000",
            "empty->smwp.content.fd-d": {
                "1": [
                    "1",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "18",
                    "19",
                    "2",
                    "20",
                    "21",
                    "28",
                    "29",
                    "3",
                    "30",
                    "31",
                    "32",
                    "33",
                    "35",
                    "36",
                    "37",
                    "38",
                    "39",
                    "4",
                    "40",
                    "49",
                    "5",
                    "50",
                    "51",
                    "52",
                    "53",
                    "54",
                    "55",
                    "56",
                    "57",
                    "58",
                    "59",
                    "6",
                    "7",
                    "8",
                    "9"
                ]
            },
            "empty->smwp.content.a-mt-scm_cnt": "empty",
            "empty->smwp.content.a-mt": {
                "1": [
                    "1",
                    "2"
                ]
            },
            "empty->smwp.content.author-info-scm_cnt": "empty",
            "empty->smwp.content.author-info": {
                "1": [
                    "1",
                    "2"
                ]
            },
            "empty->smwp.content.content-delivery-scm_cnt": "9012.6004",
            "empty->smwp.content.content-delivery": {
                "1": [
                    "1",
                    "2",
                    "3",
                    "5"
                ]
            },
            "empty->smwp.content.fd-comments-scm_cnt": "empty",
            "empty->smwp.content.fd-comments": {
                "1": [
                    "1"
                ]
            },
            "empty->smwp.content.nav-comments-scm_cnt": "empty",
            "empty->smwp.content.nav-comments": {
                "1": [
                    "1"
                ]
            },
            "empty->smwp.content.fx-scm_cnt": "empty",
            "empty->smwp.content.fx": {
                "1": [
                    "1",
                    "2"
                ]
            },
            "empty->smwp.content.comment-reply-scm_cnt": "empty",
            "empty->smwp.content.comment-reply": {
                "1": [
                    "3",
                    "4",
                    "5",
                    "6",
                    "avatar"
                ]
            },
            "empty->smwp.content.a-mb-scm_cnt": "empty",
            "empty->smwp.content.a-mb": {
                "1": [
                    "1",
                    "2"
                ]
            },
            "empty->smwp.content.0-scm_cnt": "empty",
            "empty->smwp.content.0": {
                "1": [
                    "0"
                ]
            },
            "empty->smwp.content.footer-scm_cnt": "empty",
            "empty->smwp.content.footer": {
                "1": [
                    "2",
                    "3",
                    "fb"
                ]
            },
            "empty->smwp.content.navmap-scm_cnt": "have",
            "empty->smwp.content.navmap": {
                "1": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8"
                ]
            },
            "empty->smwp.content.tt-search-scm_cnt": "empty",
            "empty->smwp.content.tt-search": {
                "1": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6"
                ]
            }
        },
        "action_rules": {
            "smwp.content.0->8991": 1,
            "smwp.content.0->3403": 1,
            "smwp.content.0->7203": 5,
            "smwp.content.0->3405": 1,
            "smwp.content.0->8256": 1,
            "smwp.content.0->7202": 8,
            "smwp.content.0->7201": 8,
            "smwp.content.0->9910": 8,
            "smwp.content.0->8464": 1,
            "smwp.content.0->8376": 1,
            "smwp.content.0->10216": 8,
            "smwp.content.0->10478": 1,
            "smwp.content.0->9631": 1
        }
    },
    "conclusion": {
        "pv_rules": [
            "由 empty 到 smwp.content.0 的PV，上报：1次"
        ],
        "ev_rules": [
            "empty 曝光 27 条数据，他们由 empty 转化而来，其中出现 27 次的d码有：['empty']，这些数据曝光没有scm推荐值。",
            "smwp.content.nav 曝光 5 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['3', '4', '5']，2 次的d码有：['2']，这些数据曝光没有scm推荐值。",
            "smwp.content.fd-d 曝光 43 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '10', '11', '12', '13', '14', '15', '16', '18', '19', '2', '20', '21', '28', '29', '3', '30', '31', '32', '33', '35', '36', '37', '38', '39', '4', '40', '49', '5', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '6', '7', '8', '9']，这些数据曝光由 9010.8000 推荐而来。",
            "smwp.content.a-mt 曝光 2 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2']，这些数据曝光没有scm推荐值。",
            "smwp.content.author-info 曝光 2 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2']，这些数据曝光没有scm推荐值。",
            "smwp.content.content-delivery 曝光 4 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2', '3', '5']，这些数据曝光由 9012.6004 推荐而来。",
            "smwp.content.fd-comments 曝光 1 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1']，这些数据曝光没有scm推荐值。",
            "smwp.content.nav-comments 曝光 1 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1']，这些数据曝光没有scm推荐值。",
            "smwp.content.fx 曝光 2 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2']，这些数据曝光没有scm推荐值。",
            "smwp.content.comment-reply 曝光 5 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['3', '4', '5', '6', 'avatar']，这些数据曝光没有scm推荐值。",
            "smwp.content.a-mb 曝光 2 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2']，这些数据曝光没有scm推荐值。",
            "smwp.content.0 曝光 1 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['0']，这些数据曝光没有scm推荐值。",
            "smwp.content.footer 曝光 3 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['2', '3', 'fb']，这些数据曝光没有scm推荐值。",
            "smwp.content.navmap 曝光 8 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2', '3', '4', '5', '6', '7', '8']，这些数据曝光有scm推荐值。",
            "smwp.content.tt-search 曝光 6 条数据，他们由 empty 转化而来，其中出现 1 次的d码有：['1', '2', '3', '4', '5', '6']，这些数据曝光没有scm推荐值。"
        ],
        "action__rules": [
            "在 smwp.content.0 页面，上报点击事件：8991 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：3403 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：7203 ，共计5次",
            "在 smwp.content.0 页面，上报点击事件：3405 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：8256 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：7202 ，共计8次",
            "在 smwp.content.0 页面，上报点击事件：7201 ，共计8次",
            "在 smwp.content.0 页面，上报点击事件：9910 ，共计8次",
            "在 smwp.content.0 页面，上报点击事件：8464 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：8376 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：10216 ，共计8次",
            "在 smwp.content.0 页面，上报点击事件：10478 ，共计1次",
            "在 smwp.content.0 页面，上报点击事件：9631 ，共计1次"
        ]
    }
}