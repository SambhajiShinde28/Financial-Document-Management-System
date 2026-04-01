from __future__ import annotations

from typing import Any

import requests
import streamlit as st


st.set_page_config(
    page_title="Financial Document Manager",
    page_icon="FD",
    layout="wide",
)


API_DEFAULT_URL = "http://127.0.0.1:8000"
DOCUMENT_TYPES = ["report", "invoice", "contract", "agreement", "other"]


def init_state() -> None:
    defaults = {
        "api_base_url": API_DEFAULT_URL,
        "token": "",
        "current_user_email": "",
        "last_response": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def auth_headers() -> dict[str, str]:
    token = st.session_state.get("token", "").strip()
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def build_url(path: str) -> str:
    base_url = st.session_state["api_base_url"].rstrip("/")
    return f"{base_url}{path}"


def handle_response(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text}

    payload = {
        "status_code": response.status_code,
        "ok": response.ok,
        "data": data,
    }
    st.session_state["last_response"] = payload
    return payload


def api_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        response = requests.request(
            method=method,
            url=build_url(path),
            headers=auth_headers(),
            json=json,
            params=params,
            data=data,
            files=files,
            timeout=60,
        )
    except requests.RequestException as exc:
        error_payload = {
            "status_code": None,
            "ok": False,
            "data": {"detail": str(exc)},
        }
        st.session_state["last_response"] = error_payload
        return error_payload

    return handle_response(response)


def show_feedback(result: dict[str, Any], success_message: str) -> None:
    if result["ok"]:
        st.success(success_message)
    else:
        detail = result["data"]
        st.error(detail.get("detail", detail))


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## Control Panel")
        st.text_input("API Base URL", key="api_base_url")

        if st.session_state["token"]:
            st.success("Authorized session is active.")
            st.caption(st.session_state["current_user_email"] or "Logged in user")
            if st.button("Clear session", use_container_width=True):
                st.session_state["token"] = ""
                st.session_state["current_user_email"] = ""
                st.rerun()
        else:
            st.info("Login or register to unlock protected actions.")

        st.markdown("---")
        st.caption("Run the API first with `uvicorn app.main:app --reload`.")


def render_hero() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(21, 110, 99, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(198, 120, 33, 0.14), transparent 24%),
                linear-gradient(180deg, #f7f4ee 0%, #efe8dc 100%);
        }
        .panel {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(74, 74, 74, 0.08);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 34px rgba(51, 45, 31, 0.08);
        }
        .eyebrow {
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #8a6c43;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .hero-title {
            color: #193d3a;
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .hero-copy {
            color: #4a4a4a;
            font-size: 1rem;
            line-height: 1.7;
        }
        </style>
        <div class="panel">
            <div class="eyebrow">Financial Workspace</div>
            <div class="hero-title">Document Operations, Access Control, and Semantic Search</div>
            <div class="hero-copy">
                Use this dashboard to register users, assign roles, upload documents,
                build vector indexes, and run financial semantic search from one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_auth_section() -> None:
    st.markdown("### Authentication")
    register_col, login_col = st.columns(2, gap="large")

    with register_col:
        with st.container(border=True):
            st.markdown("#### Register")
            with st.form("register_form", clear_on_submit=False):
                full_name = st.text_input("Full name", value="Sambhaji Shinde")
                email = st.text_input("Email", value="sambhaji@example.com")
                password = st.text_input("Password", type="password", value="Sambhaji@123")
                submitted = st.form_submit_button("Create account", use_container_width=True)

            if submitted:
                result = api_request(
                    "POST",
                    "/auth/register",
                    json={
                        "full_name": full_name,
                        "email": email,
                        "password": password,
                    },
                )
                if result["ok"]:
                    st.session_state["token"] = result["data"]["access_token"]
                    st.session_state["current_user_email"] = email
                show_feedback(result, "Account created and authorized.")

    with login_col:
        with st.container(border=True):
            st.markdown("#### Login")
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Login email", value="sambhaji@example.com")
                password = st.text_input("Login password", type="password", value="Sambhaji@123")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                result = api_request(
                    "POST",
                    "/auth/login",
                    json={"email": email, "password": password},
                )
                if result["ok"]:
                    st.session_state["token"] = result["data"]["access_token"]
                    st.session_state["current_user_email"] = email
                show_feedback(result, "Login successful.")


def render_roles_section() -> None:
    st.markdown("### Roles And Permissions")
    create_col, assign_col, inspect_col = st.columns(3, gap="large")

    with create_col:
        with st.container(border=True):
            st.markdown("#### Create role")
            with st.form("role_form"):
                role_name = st.text_input("Role name", value="Manager")
                permissions_text = st.text_area(
                    "Permissions",
                    value="documents:create\ndocuments:read\ndocuments:index",
                    help="Enter one permission per line.",
                )
                submitted = st.form_submit_button("Create role", use_container_width=True)

            if submitted:
                permissions = [item.strip() for item in permissions_text.splitlines() if item.strip()]
                result = api_request(
                    "POST",
                    "/roles/create",
                    json={"name": role_name, "permissions": permissions},
                )
                show_feedback(result, "Role created successfully.")

    with assign_col:
        with st.container(border=True):
            st.markdown("#### Assign role")
            with st.form("assign_role_form"):
                user_id = st.number_input("User ID", min_value=1, value=1, step=1)
                role_name = st.text_input("Role to assign", value="Financial Analyst")
                submitted = st.form_submit_button("Assign role", use_container_width=True)

            if submitted:
                result = api_request(
                    "POST",
                    "/users/assign-role",
                    json={"user_id": int(user_id), "role_name": role_name},
                )
                show_feedback(result, "Role assigned successfully.")

    with inspect_col:
        with st.container(border=True):
            st.markdown("#### Inspect access")
            lookup_user_id = st.number_input("Inspect user ID", min_value=1, value=1, step=1, key="inspect_user")
            role_button, permission_button = st.columns(2)

            with role_button:
                if st.button("Get roles", use_container_width=True):
                    result = api_request("GET", f"/users/{int(lookup_user_id)}/roles")
                    show_feedback(result, "Fetched roles.")

            with permission_button:
                if st.button("Get permissions", use_container_width=True):
                    result = api_request("GET", f"/users/{int(lookup_user_id)}/permissions")
                    show_feedback(result, "Fetched permissions.")


def render_document_section() -> None:
    st.markdown("### Documents")
    upload_col, browse_col, delete_col = st.columns([1.2, 1.1, 0.9], gap="large")

    with upload_col:
        with st.container(border=True):
            st.markdown("#### Upload document")
            with st.form("upload_form"):
                title = st.text_input("Title", value="Q4 Revenue Report")
                company_name = st.text_input("Company name", value="ABC Finance Ltd")
                document_type = st.selectbox("Document type", DOCUMENT_TYPES, index=0)
                uploaded_file = st.file_uploader("Select file", type=["pdf", "txt", "md"])
                submitted = st.form_submit_button("Upload", use_container_width=True)

            if submitted:
                if uploaded_file is None:
                    st.error("Please choose a PDF, TXT, or MD file.")
                else:
                    result = api_request(
                        "POST",
                        "/documents/upload",
                        data={
                            "title": title,
                            "company_name": company_name,
                            "document_type": document_type,
                        },
                        files={
                            "file": (
                                uploaded_file.name,
                                uploaded_file.getvalue(),
                                uploaded_file.type or "application/octet-stream",
                            )
                        },
                    )
                    show_feedback(result, "Document uploaded successfully.")

    with browse_col:
        with st.container(border=True):
            st.markdown("#### List and search documents")
            title = st.text_input("Search by title", key="search_title")
            company_name = st.text_input("Search by company", key="search_company")
            document_type = st.text_input("Search by type", key="search_type")
            uploaded_by = st.text_input("Uploaded by user id", key="search_uploaded_by")

            action_col, refresh_col = st.columns(2)
            with action_col:
                if st.button("Run search", use_container_width=True):
                    params = {
                        "title": title or None,
                        "company_name": company_name or None,
                        "document_type": document_type or None,
                        "uploaded_by": int(uploaded_by) if uploaded_by.strip() else None,
                    }
                    params = {key: value for key, value in params.items() if value is not None}
                    result = api_request("GET", "/documents/search", params=params)
                    show_feedback(result, "Search completed.")

            with refresh_col:
                if st.button("List all documents", use_container_width=True):
                    result = api_request("GET", "/documents")
                    show_feedback(result, "Documents loaded.")

    with delete_col:
        with st.container(border=True):
            st.markdown("#### Remove document")
            document_id = st.number_input("Document ID", min_value=1, value=1, step=1, key="delete_doc")
            if st.button("Delete document", use_container_width=True):
                result = api_request("DELETE", f"/documents/{int(document_id)}")
                show_feedback(result, "Document deleted.")


def render_rag_section() -> None:
    st.markdown("### Semantic Search")
    index_col, search_col, context_col = st.columns(3, gap="large")

    with index_col:
        with st.container(border=True):
            st.markdown("#### Index a document")
            document_id = st.number_input("Document to index", min_value=1, value=1, step=1, key="index_doc")
            if st.button("Index document", use_container_width=True):
                result = api_request("POST", "/rag/index-document", json={"document_id": int(document_id)})
                show_feedback(result, "Document indexed.")

            if st.button("Remove embedding", use_container_width=True):
                result = api_request("DELETE", f"/rag/remove-document/{int(document_id)}")
                show_feedback(result, "Vector entry removed.")

    with search_col:
        with st.container(border=True):
            st.markdown("#### Ask a financial query")
            query = st.text_area(
                "Semantic query",
                value="financial risk related to high debt ratio",
                height=120,
            )
            top_k = st.slider("Top results", min_value=1, max_value=10, value=5)
            if st.button("Run semantic search", use_container_width=True):
                result = api_request(
                    "POST",
                    "/rag/search",
                    json={"query": query, "top_k": int(top_k)},
                )
                show_feedback(result, "Semantic search completed.")

    with context_col:
        with st.container(border=True):
            st.markdown("#### Related context")
            document_id = st.number_input("Document for context", min_value=1, value=1, step=1, key="context_doc")
            if st.button("Get context", use_container_width=True):
                result = api_request("GET", f"/rag/context/{int(document_id)}")
                show_feedback(result, "Context loaded.")


def render_last_response() -> None:
    st.markdown("### Response Viewer")
    payload = st.session_state.get("last_response")
    if not payload:
        st.info("Your latest API response will appear here.")
        return

    status_col, body_col = st.columns([0.8, 2.2], gap="large")
    with status_col:
        with st.container(border=True):
            st.metric("Status", payload["status_code"] if payload["status_code"] is not None else "Error")
            st.write("Success" if payload["ok"] else "Failed")

    with body_col:
        with st.container(border=True):
            data = payload["data"]
            if isinstance(data, list):
                st.dataframe(data, use_container_width=True)
            else:
                st.json(data)


def main() -> None:
    init_state()
    render_sidebar()
    render_hero()

    top_col, stats_col = st.columns([2.2, 1], gap="large")
    with top_col:
        render_auth_section()
    with stats_col:
        with st.container(border=True):
            st.markdown("### Session")
            st.write(f"API: `{st.session_state['api_base_url']}`")
            st.write(
                "Token loaded"
                if st.session_state["token"]
                else "No token stored yet"
            )
            if st.session_state["current_user_email"]:
                st.write(f"User: `{st.session_state['current_user_email']}`")

    render_roles_section()
    render_document_section()
    render_rag_section()
    render_last_response()


if __name__ == "__main__":
    main()
