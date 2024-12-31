var user_manager = `

function userList(result) {

    let rows = "";
    console.log('result.length:', result.length)
    console.log('Array.isArray(result):', Array.isArray(result))

    $("#user_list").empty(); // 기존 내용 제거

    // 결과가 배열일 경우
    if (result.length != 0) {
      result.forEach((user) => {
        rows += \`<tr data-id="\${user.id}" onclick="viewUser(\${user.id})">
                    <td><input type="checkbox" class="select_user" data-id="\${user.id}"></td>
                    <td>\${user.id}</td>
                    <td>\${user.username}</td>
                    <td>\${user.user_id}</td>
                    <td>\${user.start_dt}</td>
                  </tr>\`;
      });
    } else {
      // 단일 객체일 경우 처리
      const user = result; // 단일 사용자 객체
      rows += \`<tr data-id="\${user.id}" onclick="viewUser(\${user.id})">
                  <td><input type="checkbox" class="select_user" data-id="\${user.id}"></td>
                  <td>\${user.id}</td>
                  <td>\${user.username}</td>
                  <td>\${user.user_id}</td>
                  <td>\${user.start_dt}</td>
                </tr>\`;
    }

    return rows
  }

  function fetchUsers() {
    $.get("/users/list", function (data) {
      let rows = "";
      //console.log('data:', data)
      const result = data.results;
      console.log('result:', result)

      // 결과가 없을 때 처리
      if (result.length === 0) {
        rows = \`<tr><td colspan="5">사용자가 없습니다.</td></tr>\`; // 사용자 없음 메시지
        $("#user_list").html(rows);
        return; // 더 이상 진행하지 않음
      }

      rows = userList(result)
      $("#user_list").html(rows);

    }).fail(function () {
      alert("사용자 목록을 가져오는 데 오류가 발생했습니다."); // 오류 메시지
    });
  }

  function search() {
    const username = $("#search_username").val(); // 사용자 이름 검색 조건
    const userId = $("#search_userid").val(); // 사용자 ID 검색 조건
    const startDt = $("#search_start_dt").val(); // 가입 날짜 검색 조건

    console.log("username:", username);
    console.log("userId:", userId);
    console.log("start_dt:", startDt);

    // AJAX 요청을 통해 사용자 목록을 필터링하여 가져오기
    $.ajax({
      url: "/users/list", // 사용자 목록을 가져오는 엔드포인트
      method: "GET",
      data: {
        username: username,
        user_id: userId,
        start_dt: startDt,
      },
      success: function (data) {
        let rows = "";
        console.log('data:', data)
        rows = userList(data.results)
        console.log('rows:', rows)
        $("#user_list").html(rows); // 사용자 목록 업데이트
      },
      error: function () {
        alert("Error fetching users!"); // 오류 메시지
      },
    });
  }

  function viewUser(id) {
    $.get(\`/users/\${id}\`, function (user) {
      console.log('user.created_at:', user.created_at);
      $("#detail_username").val(user.username);
      $("#detail_userid").val(user.user_id);
      $("#detail_start_dt").val(user.start_dt);
      $("#detail_email").val(user.email);
      $("#detail_password").val(user.password);
    });
  }

  function deleteSelectedUsers() {
    const selectedIds = [];
    $(".select_user:checked").each(function () {
      selectedIds.push($(this).data("id"));
    });

    if (selectedIds.length === 0) {
      alert("No users selected!");
      return;
    }

    if (
      confirm(
        \`Are you sure you want to delete \${selectedIds.length} users?\`
      )
    ) {
      selectedIds.forEach((id) => {
        $.ajax({
          url: \`/users/\${id}\`,
          method: "DELETE",
          success: function () {
            fetchUsers();
          },
        });
      });
      alert('users deleted!');
    }
  }

  $("#delete_selected_button").click(function () {
    deleteSelectedUsers();
  });

  $("#select_all").change(function () {
    $(".select_user").prop("checked", this.checked);
  });

  $("#save_button").click(function () {
    const id = $("#detail_userid").val();
    const payload = {
      user_id: $("#detail_userid").val(),
      username: $("#detail_username").val(),
      email: $("#detail_email").val(),
      password: $("#detail_password").val(),
      start_dt: $("#detail_start_dt").val(),
    };

    if (id) {
      // Update existing user
      $.ajax({
        url: \`/users/save\`,
        method: "post",
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function () {
          alert("User infomation success Saved!");
          fetchUsers();
        },
        error: function (xhr) {
          alert("Error: " + xhr.responseJSON.detail);  // 오류 메시지 표시
        },            
      });
    
    } else {
      // Create new user
      //payload.user_id = prompt("Enter a new User ID:");
      $.post("/users", JSON.stringify(payload), function () {
        alert("User created!");
        fetchUsers();
      }).fail(function (xhr) {
        alert("Error: " + xhr.responseJSON.detail);  // 오류 메시지 표시
      });
    }
  });

  $("#new_button").click(function () {
    $("#detail_username").val("");
    $("#detail_userid").val("");
    $("#detail_password").val("");
    $("#detail_email").val("");
    $("#detail_start_dt").val("");
    $("#detail_username").focus();
  });

  $("#search_button").click(function () {
    // fetchUsers(); // Add search logic if needed
    search();
  });

  $(document).ready(function () {
    console.log('user_manager -------------------------1');
    fetchUsers();
  });

`;