from flask import Flask, render_template, redirect, request, flash, url_for
import requests

app = Flask(__name__)
app.secret_key = 'azerty123'
base_url = "http://localhost:13500/api"

#########################
###    Utilisateurs   ###
#########################

@app.route('/')
def index():
    response_users = requests.get(f"{base_url}/users")
    
    if response_users.status_code == 200:
        users_data = response_users.json()
        return render_template("users.html", users=users_data)
    else:
        return "Failed to fetch users"

@app.route('/users')
def users():
    response_users = requests.get(f"{base_url}/users")
    
    if response_users.status_code == 200:
        users_data = response_users.json()
        return render_template("users.html", users=users_data)
    else:
        return "Failed to fetch users"


@app.route('/user/<string:username>')
def user(username):
    response = requests.get(f"{base_url}/user/{username}")

    if response.status_code == 200:
        user_data = response.json()
        return render_template("user.html", user=user_data)
    else:
        return f"Failed to fetch information for user {username}"


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'GET':
        return render_template("add_user.html")
    elif request.method == 'POST':
        full_name: str = request.form.get('fullname')
        username: str = request.form.get('username')
        passwd: str = request.form.get('passwd')
        homedir: str = request.form.get('homedir')
        shell: str = request.form.get('shell')

        if not full_name or not username or not homedir or not shell:
            flash('All fields are required', 'error')
            return redirect('/add_user')

        response = requests.post(f"{base_url}/user/add", json=
                                 {"fullname": full_name,
                                  "username": username,
                                  "homedir": homedir,
                                  "shell": shell,
                                  "passwd": passwd}
        )

        if response.status_code == 200:
            flash('User added successfully', 'success')
            return redirect('/users')
        else:
            flash('Failed to add user', 'error')
            return redirect('/add_user')
    else:
        flash('Method Not Allowed', 'error')
        return redirect('/add_user')


@app.route('/delete_user_request', methods=['GET'])
def delete_user_request():
    if request.method == 'GET':
        username: str = request.args.get('username')

        if not username:
            flash('Username is required', 'error')
            return redirect('/users')

        response = requests.delete(f"{base_url}/user/{username}")

        if response.status_code == 200:
            flash('User deleted successfully', 'success')
            return redirect('/users')
        else:
            flash('Failed to delete user', 'error')
            return redirect('/users')
    else:
        flash('Method Not Allowed', 'error')
        return redirect('/users')

@app.route('/update_user', methods=['POST'])
def update_user():
    if request.method == 'POST':
        full_name: str = request.form.get('fullname')
        homedir: str = request.form.get('homedir')
        username: str = request.form.get('username')
        shell: str = request.form.get('shell')
        passwd: str = request.form.get('passwd')

        if not full_name or not homedir or not shell:
            flash('All fields except password are required', 'error')
            return redirect(f'/users')

        user_data: dict = {
            "fullname": full_name,
            "homedir": homedir,
            "shell": shell,
            "passwd": passwd
        }

        # Send update request to the backend API
        response = requests.put(f"{base_url}/user/{username}", json=user_data)

        print(response.json())

        if response.status_code == 200:
            flash('User updated successfully', 'success')
            return redirect(url_for('users'))
        else:
            flash('Failed to update user', 'error')
            return redirect(f'/update_user/{username}')
    else:
        flash('Method Not Allowed', 'error')
        return redirect(url_for('users'))

#########################
###      Groupes      ###
#########################

@app.route('/groups')
def groups():
    response_groups = requests.get(f"{base_url}/groups")
    
    if response_groups.status_code == 200:
        groups_data = response_groups.json()
        return render_template("groups.html", groups=groups_data)
    else:
        return "Failed to fetch groups"


@app.route('/add_member', methods=['POST'])
def add_member_to_group():
    if request.method == 'POST':
        groupname = request.form.get('groupname')
        user = request.form.get('user')

        if not groupname or not user:
            flash("Group name and user are required", "error")
            return redirect(url_for('groups'))

        response = requests.post(f"{base_url}/member/add", json={"groupname": groupname, "users": [user]})

        if response.status_code == 200:
            flash("Member added successfully", "success")
            return redirect(url_for('groups'))
        else:
            flash("Failed to add member", "error")
            return redirect(url_for('groups'))
    else:
        flash("Method Not Allowed", "error")
        return redirect(url_for('groups'))


@app.route('/delete_member', methods=['POST'])
def delete_member_from_group():
    if request.method == 'POST':
        groupname = request.form.get('groupname')
        user = request.form.get('memberName')

        if not groupname or not user:
            flash("Group name and user are required", "error")
            return redirect(url_for('groups'))

        response = requests.delete(f"{base_url}/member/del", json={"groupname": groupname, "users": [user]})

        if response.status_code == 200:
            flash("Member deleted successfully", "success")
            return redirect(url_for('groups'))
        else:
            flash("Failed to delete member", "error")
            return redirect(url_for('groups'))
    else:
        flash("Method Not Allowed", "error")
        return redirect(url_for('groups'))


@app.route('/add_group', methods=['GET', 'POST'])
def add_group():
    if request.method == 'GET':
        return render_template("add_group.html")
    elif request.method == 'POST':
        groupname = request.form.get('groupname')

        if not groupname:
            flash("Group name is required", "error")
            return redirect(url_for('add_group'))

        response = requests.post(f"{base_url}/group/add", json={"groupname": groupname})

        if response.status_code == 200:
            flash("Group added successfully", "success")
            return redirect(url_for('groups'))
        else:
            flash("Failed to add group", "error")
            return redirect(url_for('groups'))
    else:
        return "Method Not Allowed", 405


@app.route('/delete_group', methods=['GET'])
def delete_group():
    if request.method == 'GET':
        groupname = request.args.get('groupname')

        if not groupname:
            flash("Group name is required", "error")
            return redirect(url_for('groups'))

        response = requests.delete(f"{base_url}/group/del?groupname={groupname}")

        if response.status_code == 200:
            flash("Group deleted successfully", "success")
            return redirect(url_for('groups'))
        else:
            flash("Failed to delete group", "error")
            return redirect(url_for('groups'))
    else:
        return "Method Not Allowed", 405

#########################
###      Main         ###
#########################

if __name__ == '__main__':
    app.run(debug=True)

