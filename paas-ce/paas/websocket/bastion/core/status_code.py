class WebSocketStatusCode:
    """
    errorArr: [
        { key: 1, errorMsg: '您的访问令牌无法通过授权，请尝试重新登录或联系管理员' },
        { key: 2, errorMsg: '用户认证失败，请退出后重新连接。' },
        { key: 3, errorMsg: '访问策略未通过，请联系管理员后重试。' },
        { key: 4, errorMsg: '主机资源类型错误，请联系管理员。' },
        { key: 5, errorMsg: '连接超时，请退出后重新连接。' },
        { key: 6, errorMsg: '凭证验证失败，请联系管理员。' },
        { key: 7, errorMsg: '创建连接失败，请退出后重新连接。' },
        { key: 8, errorMsg: '目前不支持该类型数据库。' },
        { key: 9, errorMsg: '无法连接到代理服务器。' },
        { key: 10, errorMsg: '连接服务器失败或登录认证失败。' },
        { key: 11, errorMsg: '当前主机已不存在，请刷新列表后重试。' },
        { key: 12, errorMsg: '当前凭证已不存在，请刷新列表后重试。' },
        { key: 13, errorMsg: '目标主机连接被拒(可能是网络或端口问题)。' },
        { key: 14, errorMsg: '与目标主机创建连接失败。' },
        { key: 15, errorMsg: '创建连接失败，请联系管理员处理。' },
        { key: 16, errorMsg: 'SSH凭证解析失败，请检查私钥后重试。' },
    ],
    """
    base = "ws_errcode:"
    PARAM_ERROR = f"{base}1"                        # 您的访问令牌无法通过授权，请尝试重新登录或联系管理员。 参数错误，一般指Token错误
    USER_ERROR = f"{base}2"                         # 用户认证失败，请退出后重新连接。 校验用户错误，即登录用户与当前请求用户不是同一用户
    ACCESS_ERROR = f"{base}3"                       # 访问策略未通过，请联系管理员后重试。 您的当次访问已不符合访问策略要求 (其实就是超过了访问时间的时间段)
    HOST_TYPE_ERROR = f"{base}4"                    # 主机资源类型错误，请联系管理员。 您选择的主机不支持SSH协议 主机类型错误
    TIME_OUT = f"{base}5"                           # 连接超时，请退出后重新连接。
    SSH_AUTH_FAILED_ERROR = f"{base}6"              # 凭证验证失败，请联系管理员。SSH验证失败，请校验您输入的密码或联系管理员确认凭证内容
    CHANNEL_CREATE_ERROR = f"{base}7"               # 创建连接失败，请退出后重新连接。Channel创建失败
    DATABASE_TYPE_ERROR = f"{base}8"                # 目前不支持该类型数据库。数据库类型错误
    PROXY_LINK_ERROR = f"{base}9"                   # 无法连接到代理服务器。 Proxy连接失败
    SSH_LINK_ERROR = f"{base}10"                    # 连接服务器失败或登录认证失败。
    HOST_NOT_FOUND_ERROR = f"{base}11"              # 当前主机已不存在。
    CRED_NOT_FOUND_ERROR = f"{base}12"              # 当前凭证已不存在。
    TARGET_HOST_RESET_PEER_ERROR = f"{base}13"      # 目标主机连接被拒(可能是网络问题或端口问题)。
    TARGET_HOST_SSH_ERROR = f"{base}14"             # 与目标主机创建连接失败。
    CLIENT_SSH_ERROR = f"{base}15"                  # 创建连接失败，请联系管理员处理。
    SSH_KEY_ENCRYPTED_ERROR = f"{base}16"           # SSH凭证解析失败，请检查私钥后重试。


class MySQLWebSocketStatusCode:
    # 参数错误，一般指Token错误
    PARAM_ERROR = {"data_type": "error", "message": "您的访问令牌无法通过验证，请尝试重新登录或联系管理员"}
    # 校验用户错误，即登录用户与当前请求用户不是同一用户
    USER_ERROR = {"data_type": "error", "message": "用户校验失败，请尝试重新登录或者联系管理员"}
    # 没有通过访问策略
    ACCESS_ERROR = {"data_type": "error", "message": "您的当次访问已不符合访问策略要求"} # (其实就是超过了访问时间的时间段)
    # 主机类型错误
    HOST_TYPE_ERROR = {"data_type": "error", "message": "您的当次访问已不符合访问策略要求"}  # 您选择的主机不支持SSH协议
    # 连接超时
    TIME_OUT = {"data_type": "error", "message": "数据库连接超时，请稍后再试或联系管理员"}
    # 断开连接
    LEAVE_TIME_OUT = {"data_type": "error", "message": "数据库长时间未操作，断开连接!"}
    # 数据库网络代理失败
    DATABASE_PROXY_ERROR = {"data_type": "error", "message": "数据库代理连接失败，请校验代理信息或联系管理员确认代理相关配置"}
    # 数据库验证失败
    DATABASE_CHECK_ERROR = {"data_type": "error", "message": "数据库验证失败，请校验您输入的密码或联系管理员确认凭证内容"}
    # 数据库处理失败
    DATA_CHECK_ERROR = {"data_type": "error", "message": "数据处理失败，请重新登录或联系管理员处理"}
    LINK_DATA_CHECK_ERROR = {"data_type": "error", "message": "连接错误，请重新登录或联系管理员处理: "}
    # 用户没有权限
    USER_PERMISSIONS_ERROR = {"data_type": "error", "message": "用户没有相关权限，请联系管理员或授权后重试: "}
    # Channel创建失败
    CHANNEL_CREATE_ERROR = {"data_type": "error", "message": "服务器出现了一点小问题，请稍后再试或联系管理员"}
    # 数据库类型错误
    DATABASE_TYPE_ERROR = {"data_type": "error", "message": "目前不支持该类型数据库"}
    # Proxy连接失败
    PROXY_LINK_ERROR = {"data_type": "error", "message": "无法连接到代理服务器"}
    SERVER_ERROR = {"data_type": "error", "message": "异常退出：{}"}
    CLOSE_SUCCESS = {"data_type": "close", "message": "退出"}
