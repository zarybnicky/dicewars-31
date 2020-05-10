with import <nixpkgs> {};
with python37Packages; buildPythonApplication {
  name = "dicewars-31";
  propagatedBuildInputs = [
    numpy
    pyqt5
    matplotlib
    pytorch
    tensorflow-tensorboard
    Keras
    (buildPythonPackage rec {
      pname = "hexutil";
      version = "0.2.2";
      src = fetchPypi {
        inherit pname version;
        sha256 = "0vxs1ij0rqygvgwi0r08q0hma2bxhf58gdh4lanpabym1r6xxq34";
      };
    })
  ];
}
