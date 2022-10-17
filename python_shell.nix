{lib, buildPythonPackage, 
    pytestCheckHook,
    numpy, 
    scipy, 
    pip,
    matplotlib,
}:

buildPythonPackage rec {
    pname = "example_name";
    version = "0.0.1";
    src = ./.;
    format = "pyproject";
    checkInputs = [ pytestCheckHook ];
    buildInputs = [pip];
    propagatedBuildInputs = [
        numpy
        scipy
        matplotlib
    ];
    meta = with lib; {
        # homepage = "https://github.com/pytoolz/toolz";
        # description = "List processing tools and functional utilities";
        # license = licenses.bsd3;
        # maintainers = with maintainers; [ fridh ];
    };
}
