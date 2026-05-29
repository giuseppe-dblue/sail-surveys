import streamlit as st


def check_password() -> bool:
    def _submit() -> None:
        if st.session_state["pwd_input"] == st.secrets["password"]:
            st.session_state["authenticated"] = True
        else:
            st.session_state["auth_failed"] = True

    if st.session_state.get("authenticated"):
        return True

    st.title("SAIL Survey Analysis")
    st.text_input("Password", type="password", key="pwd_input", on_change=_submit)
    if st.session_state.get("auth_failed"):
        st.error("Incorrect password — please try again.")
    return False
