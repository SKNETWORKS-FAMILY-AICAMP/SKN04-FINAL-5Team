
var docu_list = `
    function loadDocuments() {
        const searchQuery = document.getElementById('searchQuery').value;
        // AJAX 요청 (조회) - GET 방식으로 변경
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: searchQuery }) // 요청 본문에 데이터를 포함
        })
        .then(response => response.json())
        .then(data => {

            //console.log('data:', data.results[0].doc_id)
            const tableBody = document.getElementById('table-body');
            tableBody.innerHTML = '';
            const result = data.results;

            result.forEach((item, index) => {
                const row = document.createElement('tr');
                console.log('item:', item.source)
                row.innerHTML = \`
                    <td><input type="checkbox" class="select-doc" data-doc-id="\${item.doc_id}"></td>
                    <td>\${index + 1}</td>
                    <td>\${item.source}</td>
                    <td>\${item.total_pages}</td>
                    <td>\${item.upload_time}</td>
                \`;

                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            alert('데이터를 불러오는 중 오류가 발생했습니다.');
        });        
    }    

    $(document).ready(function() {
        loadDocuments();  // DOM이 로드된 후 문서 목록을 불러옵니다.

        // searchButton 클릭 이벤트 리스너 추가
        $('#searchButton').on('click', function() {
            loadDocuments();  // 문서 목록을 불러오는 함수 호출
        });

        $('#deleteButton').on('click', function() {
            deleteDocument();  // 문서 목록을 불러오는 함수 호출
        });
        
        // 전체 선택 체크박스 기능
        $('#select-all').on('change', function() {
            const isChecked = $(this).prop('checked');
            $('.select-doc').prop('checked', isChecked);
        });

    });    

    // 선택된 문서를 삭제하는 함수
    function deleteDocument() {
        const selectedDocs = [];
        const checkboxes = document.querySelectorAll('.select-doc:checked');
        console.log('checkboxes:', checkboxes)
        checkboxes.forEach(checkbox => {
            selectedDocs.push(checkbox.getAttribute('data-doc-id'));  // 선택된 체크박스에서 doc_id 가져오기
        });

        if (selectedDocs.length === 0) {
            alert('삭제할 문서를 선택하세요.');
            return;
        }

        // console.log('selectedDocs:', selectedDocs)

        if (confirm('정말로 선택된 문서를 삭제하시겠습니까?')) {
            fetch('/docu_del', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ doc_ids: selectedDocs })  // 삭제할 문서 ID와 액션을 JSON으로 전송
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert(data.message);
                loadDocuments();  // 삭제 후 문서 목록을 다시 로드
            })
            .catch(error => {
                console.error('Error deleting documents:', error);
                alert('문서 삭제에 실패했습니다.');
            });
        }
    }

    // 페이지 로드 시 문서 목록을 불러옵니다.
    $(document).ready(function() {
        loadDocuments();
    });
`
