#include <Python.h>

#define BOTTOM 0
#define TOP 1

typedef struct State{
    unsigned char board[14];
    signed char turn;
} State;


static PyObject*
py_after_move(PyObject *self, PyObject *args)
{
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

    /* GAME LOGIC */

    char seeds;
    char sum_top = 0, sum_bottom = 0;
    int index;
    int skip_store;
    int opposite;

    if (!(move >= 0 && move < 6)) {
        PyErr_SetString(PyExc_IndexError, "Houses 0 through 5 only.");
        PyBuffer_Release(&view);
        return NULL;
    }

    if (state->turn == TOP){
        move += 7;
        skip_store = 6;
    }
    else {
        skip_store = 13;
    }

    seeds = state->board[move];
    if (seeds == 0) {
        PyErr_SetString(PyExc_ValueError, "No seeds in given house.");
        PyBuffer_Release(&view);
        return NULL;
    }

    // distrubute seeds
    state->board[move] = 0;
    index = move;
    while (seeds > 0) {
        index = (index+1) % 14;
        if (index != skip_store) {
            state->board[index]++;
            seeds--;
        }
    }


    // seed stealing
    if (state->board[index] == 1) {
        opposite = abs(6 - index);
        if (index < 6) {
            opposite = 6 + opposite;
        }
        else {
            opposite = 6 - opposite;
        }

        if ((state->turn == BOTTOM && (index < 6 && index >= 0)) ||
            (state->turn == TOP && (index >= 7 && index < 13))) {
            state->board[index] += state->board[opposite];
            state->board[opposite] = 0;
        }
    }

    // turn flip or extra turn
    if (index != 6 && index != 13) {
        state->turn = (++state->turn) % 2;
    }

    // sum bottom
    for (int i=0; i < 6; i++) {
        sum_bottom += state->board[i];
    }
    // sum top
    for (int i=7; i < 13; i++) {
        sum_top += state->board[i];
    }

    // game over check
    if (sum_bottom == 0 || sum_top == 0) {
        state->board[6] += sum_bottom;
        state->board[13] += sum_top;
        for (int i=0; i < 13; i++) {
            if (i != 6) {
                state->board[i] = 0;
            }
        }
        state->turn = -1;
    }

    PyBuffer_Release(&view);
    return new_buff;
}

// module method table
static PyMethodDef meths[] = {
    {"after_move", py_after_move, METH_VARARGS,
    "after_move(state._bstring, move) -> bytes\n"
    "move is the index that player state.turn wants to use. yields the resulting "
    "state _bstring"},
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
