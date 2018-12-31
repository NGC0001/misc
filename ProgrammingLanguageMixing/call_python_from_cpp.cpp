/**
 * \file
 * \brief A sample of calling python functions from C/C++ code.
 *
 * Note:
 * 1. Use python3-config to list compiling and linking configurations for python library.
 * 2. " g++ -I/usr/include/python3.6m -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu call_python_from_cpp.cpp -lpython3.6m "
 *    -lpython3.6m shall be placed after the source file.
 */

#include <iostream>
#include <vector>
#include <string>
#include <locale>
#include <codecvt>
#include <stdexcept>

#include "Python.h"

// To use numpy:
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "/usr/local/lib/python3.6/dist-packages/numpy/core/include/numpy/ndarraytypes.h"
// Reference: https://docs.scipy.org/doc/numpy-1.14.0/reference/c-api.array.html

using std::cout;
using std::endl;

std::wstring utf8string_to_wstring(const std::string& str);

std::string pythonSource{"call_python_from_cpp"}; // .py extension must be droped.
std::string funcName{"hello"};


int main(int argc, char* argv[]) try{
    std::vector<std::wstring> wargs;
    std::vector<wchar_t*> pwargs(argc+1, nullptr);
    for(int i = 0; i < argc; ++i){
        wargs.push_back(utf8string_to_wstring(std::string(argv[i])));
        pwargs[i] = &wargs[i][0];
    }
    wchar_t** wargv = &pwargs[0];

    cout << "Usage: exe_name [integers]" << endl;

    // Optional but recommended.
    Py_SetProgramName(wargv[0]);
    cout << "wchar_t program name set." << endl;

    Py_Initialize();
    cout << "python interpreter initialized." << endl;

    PySys_SetArgv(argc, wargv); // must call this to get sys.argv and relative imports.
    cout << "wchar_t argv set." << endl;

    // Build the name object.
    PyObject* pName = PyUnicode_FromString(pythonSource.c_str());
    if(!pName){
        cout << "python error for pName." << endl;
        PyErr_Print();
        throw std::runtime_error{"python error"};
    }
    else{
        cout << "python unicode object built from string: " << pythonSource << endl;
    }

    // Load the module object.
    PyObject* pModule = PyImport_Import(pName);
    if(!pModule){
        cout << "python error for pModule." << endl;
        PyErr_Print();
        throw std::runtime_error{"python error"};
    }
    else{
        cout << "imported from: " << pythonSource << endl;
    }

    // pDict is a borrowed reference(i.e., we don't own the reference),
    // so we don't need to Py_DECREF() it.
    PyObject* pDict = PyModule_GetDict(pModule);
    if(!pDict){
        cout << "python error for pDict." << endl;
        PyErr_Print();
        throw std::runtime_error{"python error"};
    }
    else{
        cout << "dictionary got." << endl;
    }

    // pFunc is also a borrowed reference.
    PyObject* pFunc = PyDict_GetItemString(pDict, funcName.c_str());
    if(!pFunc){
        cout << "python error for pFunc." << endl;
        PyErr_Print();
        throw std::runtime_error{"python error"};
    }
    else{
        cout << "function got." << endl;
    }

    if(PyCallable_Check(pFunc)){
        cout << "python callable: " << funcName << endl;
        PyObject* pValue;
        if(argc > 1){
            PyObject* pArgs = PyTuple_New(argc - 1);
            for(int i = 0; i < argc-1; ++i){
                cout << "argument " << i << ": " << argv[i+1] << endl;
                pValue = PyLong_FromLong(std::stol(argv[i+1]));
                if(!pValue){
                    cout << "python error for pValue." << endl;
                    PyErr_Print();
                    throw std::runtime_error{"python error"};
                }
                PyTuple_SetItem(pArgs, i, pValue);
            }
            pValue = PyObject_CallObject(pFunc, pArgs);
            if(pArgs != nullptr){
                cout << "extra clean up for pArgs." << endl;
                Py_DECREF(pArgs);
                pArgs = nullptr;
            }
        }
        else{
            pValue = PyObject_CallObject(pFunc, NULL);
        }
        if(pValue != nullptr){
            PyObject* pRepr = PyObject_Repr(pValue);
            PyObject* pBytes = PyUnicode_AsEncodedString(pRepr, "utf-8", "~E~");
            cout << "python callable " << funcName << " returned: " << PyBytes_AS_STRING(pBytes) << endl;
            cout << "extra clean up for pBytes and pRepr." << endl;
            Py_DECREF(pBytes);
            pBytes = nullptr;
            Py_DECREF(pRepr);
            pRepr = nullptr;

            if(true){
                PyArrayObject* pArray = reinterpret_cast<PyArrayObject*>(pValue);
                int ndim = PyArray_NDIM(pArray);
                cout << "ndarray dimension: " << ndim << endl;
                std::vector<int> shape(ndim);
                auto pshape = PyArray_DIMS(pArray);
                size_t totalSize = 1;
                for(int i = 0; i < ndim; ++i){
                    shape[i] = *pshape++;
                    totalSize *= shape[i];
                }
                cout << "ndarray shape: ";
                for(auto d : shape){
                    cout << d << ' ';
                }
                cout << endl;
                cout << "ndarray total size: " << totalSize << endl;
                double* pd = reinterpret_cast<double*>(PyArray_DATA(pArray));
                cout << "ndarray content: ";
                for(int i = 0; i < totalSize; ++i){
                    cout << pd[i] << ' ';
                }
                cout << endl;

                // Other utilities that may help: PyArray_Size, PyArray_STRIDES, PyArray_AsCArray, etc.
                // See https://docs.scipy.org/doc/numpy-1.14.0/reference/c-api.array.html for more help.
            }

            cout << "extra clean up for pValue." << endl;
            Py_DECREF(pValue);
            pValue = nullptr;
        }
        else{
            cout << "python callable " << funcName << " returned abnormally." << endl;
            PyErr_Print();
            throw std::runtime_error{"python error"};
        }
    }
    else{
        cout << "not a python callable: " << funcName << endl;
        PyErr_Print();
        throw std::runtime_error{"python error"};
    }

    // Clean up.
    pFunc = nullptr;
    pDict = nullptr;
    Py_DECREF(pModule);
    pModule = nullptr;
    Py_DECREF(pName);
    pName = nullptr;
    cout << "Python objects dereferenced." << endl;

    // Finish the Python Interpreter.
    Py_Finalize();
    cout << "python interpreter finalized." << endl;

    return 0;
}
catch(std::exception& e){
    cout << "exception: " << e.what() << endl;
    return -1;
}
catch(...){
    return -1;
}


std::wstring utf8string_to_wstring(const std::string& str){
    std::wstring_convert<std::codecvt_utf8<wchar_t>, wchar_t> converter;

    // to_bytes: wstring -> utf-8 string
    // from_bytes: utf-8 string -> wstring
    return converter.from_bytes(str);
}

