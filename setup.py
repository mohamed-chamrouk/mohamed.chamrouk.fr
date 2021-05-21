from setuptools import setup

setup(
    name='mohamed_chamrouk_fr',
    packages=['mohamed_chamrouk_fr'],
    include_package_data=True,
    install_requires=[
        'flask'
        , 'flask_sqlalchemy'
        , 'flask_migrate'
        , 'flask_login'
        , 'werkzeug'
        , 'httpagentparser'
        , 'markdown'
        , 'psycopg2-binary'
        , 'gitpython'
    ],
)
