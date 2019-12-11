import platform


def get_platform():
    """return Linux | Windows | Java | empty str """
    return platform.system()


if __name__ == '__main__':
    print(get_platform())