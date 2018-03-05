#include <Python.h>

typedef struct State{
    char board[14];
    char turn;
} State;


static PyObject *py_after_move(PyObject *self, PyObject *args){
    PyObject *buffobj;
    Py_buffer view;
    int move;

    //get the passed PyObject
    if (!PyArg_ParseTuple(args, "Oi", &buffobj, &move)) {
        return NULL;
    }

    //get buffer info
    if (PyObject_GetBuffer(buffobj, &view, PyBUF_ANY_CONTIGUOUS | PyBUF_FORMAT) == -1) {
        return NULL;
    }
    State state;
    memcpy(&state, view.buf, sizeof(state));
    for (int i=0; i < 14; i++) {
        state.board[i] += 1;
    }
    state.turn++;
    char *aschr = (char*) &state;
    return Py_BuildValue("y#", aschr, 15);
}

// module method table
static PyMethodDef meths[] = {
    {"after_move", py_after_move, METH_VARARGS,
    "move is the index that player state.turn wants to use. yields the resulting state"},
    {NULL, NULL, 0, NULL}
};

/* Module structure */
static struct PyModuleDef mod = {
  PyModuleDef_HEAD_INIT,
  "cstate",                                   /* name of module */
  "Fast C functions for state manupulation",  /* Doc string (may be NULL) */
  -1,                                         /* Size of per-interpreter state or -1 */
  meths                                       /* Method table */
};

/* Module initialization function */
PyMODINIT_FUNC
PyInit_cstate(void) {
  return PyModule_Create(&mod);
}
