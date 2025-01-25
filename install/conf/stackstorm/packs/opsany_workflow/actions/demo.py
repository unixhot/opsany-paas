from st2common.runners.base_action import Action

class Demo(Action):
    def run(self, name):
        print("name", name)
        return "OpsAny WorkFlow Info:{name}".format(name=name)

if __name__ == '__main__':
    pass
