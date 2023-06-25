from setuptools import setup, find_packages

setup(name='summersoc23',
      version='0.1.0',
      description='Services in Industry 4.0. Modeling and composition.',
      license='MIT',
      packages=find_packages(include=['aida*']),
      zip_safe=False,
      install_requires=[
            "numpy",
            "graphviz",
            "websockets",
            "paho-mqtt",
            "requests",
            "logaut",
            "pythomata",
            "networkx",
            "pydotplus",
            "datetime",
            "connexion[swagger-ui]",
            "aiohttp-jinja2",
            "mdp_dp_rl @ git+https://github.com/luusi/mdp-dp-rl.git#egg=mdp_dp_rl"
      ]
)
