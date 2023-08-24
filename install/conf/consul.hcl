acl {
   enabled = true
   default_policy = "deny"
   down_policy = "extend-cache"
   tokens = {
      master = "CONSUL_TOKEN"
   }
}
