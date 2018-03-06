#include <Python.h>

#define BOTTOM 0
#define TOP 1

typedef struct State{
    unsigned char board[14];
    signed char turn;
} State;


static PyObject *py_after_move(PyObject *self, PyObject *args){
    PyObject *old_state;
    Py_buffer view;
    PyObject *new_buff;
    int move;

    //get the passed PyObject
    if (!PyArg_ParseTuple(args, "Oi", &old_state, &move)) {
        return NULL;
    }

    //get reference to underlying buffer
    if (PyObject_GetBuffer(old_state, &view, PyBUF_ANY_CONTIGUOUS | PyBUF_FORMAT) == -1){
        return NULL;
    }

    //create new bytes object from old data
    new_buff = Py_BuildValue("y#", view.buf, view.len);
    PyBuffer_Release(&view); // free reference count

    //get buffer info of new bytes object
    if (PyObject_GetBuffer(new_buff, &view, PyBUF_ANY_CONTIGUOUS | PyBUF_FORMAT) == -1) {
        return NULL;
    }

    //address/length security
    if (view.len != sizeof(State)) {
        char buffer[50];
        sprintf(buffer, "bytestring must be %lu bytes long!", sizeof(State));
        PyErr_SetString(PyExc_TypeError, buffer);
        PyBuffer_Release(&view);
        return NULL;
    }

    // cast buffer to a state
    State *state = (State*) view.buf;

    for (int i=0; i < 14; i++) {
        state->board[i] += 1;
    }
    state->turn++;


    PyBuffer_Release(&view);
    return new_buff;
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
