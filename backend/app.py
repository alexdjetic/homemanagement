from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from typing import List
from system import get_os
from system.users import Users
from system.groups import Groups
from system.member import Member
import uvicorn
import argparse


class GroupInfo(BaseModel):
    """The group information to give"""
    groupname: str = Field(description="Name of the group", default="")
    gid: int = Field(description="gid of the group", default=-1)


class MemberInfo(BaseModel):
    """The member input info to give"""
    groupname: str = Field(description="Name of the group", default="")
    users: List[str] = Field(description="List of users", default=[])


class UserInfo(BaseModel):
    """The linux User information """
    fullname: str = Field(description="full name of the user")
    username: str = Field(description="username of the user", default="")
    passwd: str = Field(description="password of the user", default="")
    homedir: str = Field(description="The home directory of a user", default="")
    shell: str = Field(description="the shell of the user", default="/bin/bash")


app = FastAPI(
    title="my backend API for all use.",
    description="This APi mange Users and Groups of a system",
    version="0.1",
    contact={
        "name": "Alexandre Djetic",
        "email": "alexandredejtic@proton.me"
    },
)

os_name: str = get_os()
users: Users = Users(os_name)
groups: Groups = Groups(os_name)

######################
####    index     ####
######################

@app.get("/")
async def root():
    """
    Root endpoint displaying the default FastAPI documentation.
    """
    return HTMLResponse(get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation"))

######################
#### Users route #####
######################

@app.get("/api/users")
async def get_users() -> dict:
    """
    Endpoint to retrieve information about users.
    """
    return await users.get_all()


@app.get("/api/user/{user}")
async def get_user(user: str) -> dict:
    """
    Endpoint to retrieve information about users.
    """
    if not user:
        raise HTTPException(status_code=404, detail="Please provide a username.")

    return await users.get_user(user)   
    


@app.post("/api/user/add")
async def add_user(user_info: UserInfo) -> dict:
    """
    Endpoint to add a new user.
    """
    full_name: str = user_info.fullname
    username: str = user_info.username
    passwd: str = user_info.passwd
    homedir: str = user_info.homedir
    shell: str = user_info.shell

    if not username:
        raise HTTPException(status_code=400, detail="Please provide a username for the user.")

    if not homedir:
        homedir = f"/home/{username}"

    # create the user
    created: dict = await users.add_user(username, full_name, homedir, shell)

    # password
    if passwd:
        rcode: bool = await Users.assign_password(username, passwd)
        
        if rcode and created.get("status", False) == 200:
            return {
                "status": 200,
                "message": f"L'utilisateur {username}: full_name: {full_name}, homedir: {homedir}, shell: {shell} a été créé",
                "stdout": created.get("stdout", ""),
                "error": created.get("error", ""),
                "password": True
            }
        else:
            return {
                "status": created.get("status", 505),
                "message": f"L'utilisateur {username}: full_name: {full_name}, homedir: {homedir}, shell: {shell} n'a pas été créé",
                "stdout": created.get("stdout", ""),
                "error": created.get("error", ""),
                "password": True
            }
    else:
        return created


@app.delete("/api/user/{user}")
async def del_user(user: str) -> dict:
    """
    Endpoint to delete a user.
    """
    if not user:
        raise HTTPException(status_code=500, detail="Please provide a username for this user.")

    return await users.del_user(user)


@app.put("/api/user/{user}")
async def update_user(user: str, user_info: UserInfo) -> dict:
    """
    Endpoint to update user information.
    """
    full_name: str = user_info.fullname
    passwd: str = user_info.passwd
    homedir: str = user_info.homedir
    shell: str = user_info.shell

    if not user:
        raise HTTPException(status_code=404, detail="Please provide a username.")

    if not full_name:
        raise HTTPException(status_code=400, detail="Please provide a full name for the user.")

    return await users.update_user(user, full_name, passwd, homedir, shell)

#######################
#### Groups route #####
#######################

@app.get("/api/groups")
async def get_groups() -> dict:
    """
    Endpoint to retrieve information about groups.
    """
    return await groups.get_all()


@app.get("/api/group/{groupname}")
async def get_group(groupname: str) -> dict:
    """
    Endpoint to retrieve information about groups.
    """
    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname")

    return await groups.get_group(groupname)


@app.post("/api/group/add")
async def add_groups(group: GroupInfo) -> dict:
    """
    Endpoint to add a new group.
    """
    groupname: str = group.groupname

    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname")

    return await groups.add_group(groupname)


@app.delete("/api/group/del")
async def del_groups(group: GroupInfo) -> dict:
    """
    Endpoint to delete a group.
    """
    groupname: str = group.groupname

    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname for this group.")

    return await groups.del_group(groupname)

#############################
#### Groups Member route ####
#############################

@app.get("/api/member")
async def get_members(memberinfo: GroupInfo) -> dict:
    groupname: str = memberinfo.groupname

    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname for this group.")

    return await Member.get_group_members(groupname)


@app.post("/api/member/add")
async def add_members(memberinfo: MemberInfo) -> dict:
    """
    Endpoint to add members to a group.
    """
    groupname: str = memberinfo.groupname
    users: List[str] = memberinfo.users

    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname for this group.")

    success_users = []
    failed_users = []

    for user in users:
        response = await Member.add_member_to_group(groupname, user)
        if response["status"] == 200:
            success_users.append(user)
        else:
            failed_users.append(user)

    message = f"All users were successfully added to group {groupname}" if not failed_users else f"Not all users were added to group {groupname}"

    return {
        "status": 200 if not failed_users else 500,
        "message": message,
        "success_users": success_users,
        "failed_users": failed_users
    }

@app.delete("/api/member/del")
async def del_members(memberinfo: MemberInfo) -> dict:
    """
    Endpoint to remove members from a group.
    """
    groupname: str = memberinfo.groupname
    users: List[str] = memberinfo.users

    if not groupname:
        raise HTTPException(status_code=500, detail="Please provide a groupname for this group.")

    success_users = []
    failed_users = []

    for user in users:
        response = await Member.remove_member_from_group(groupname, user)
        if response["status"] == 200:
            success_users.append(user)
        else:
            failed_users.append(user)

    message = f"All users were successfully removed from group {groupname}" if not failed_users else f"Not all users were removed from group {groupname}"

    return {
        "status": 200 if not failed_users else 500,
        "message": message,
        "success_users": success_users,
        "failed_users": failed_users
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FastAPI Server")
    parser.add_argument('--port', type=int, default=13500, help="Port for the server (default: 13500)")
    parser.add_argument('--reload', action='store_true', help="Enable auto-reload (default: False)")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port, reload=args.reload)

