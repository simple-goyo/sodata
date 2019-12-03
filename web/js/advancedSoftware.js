new Vue({
    el: '#app',
    data () {
      return {
          all_code_description: [],
          query_prompt: 'query',
          query: '',
          isActive: true,
          pageCurrentData: [],
          pageData: [],
          total_api_num: 13,
          pageNum: 0,
          APIName: [],
          moreButton: false,
          current_api_num: 0,
          options: [{
            value: 'a',
            label: 'API Name'
          }, {
            value: 'b',
            label: 'Nature language'
          }],
          value: 'a',
          postUrl: 'http://127.0.0.1:5000/getAPISampleCodeByName/',
          example1: "javax.jws.WebService",
          api2graph: {}
      }
    },
    methods: {
        change_search (){
            this.query = ""
            if(this.value == 'a') {
                this.postUrl = 'http://127.0.0.1:5000/getAPISampleCodeByName/'
                this.example1 = "javax.jws.WebService"
            } else {
                this.postUrl = 'http://127.0.0.1:5000/getAPISampleCode/'
                this.example1 = "How to create a pojo class"
            }
        },
        change_data (val) {
            // console.log(val)
            let _this = this
            let current_num = (val - 1) * 5
            _this.pageCurrentData = []
            _this.current_api_num = current_num
            if (current_num + 5 > _this.all_code_description.length) {
                let num = current_num
                for (let index = 0; index < _this.all_code_description.length - num; index++){
                console.log(_this.all_code_description[current_num])
                _this.pageCurrentData[index] = _this.all_code_description[current_num]
                current_num++
                }
            } else {
                for (let index = 0; index < 5; index++){
                _this.pageCurrentData[index] = _this.all_code_description[current_num]
                current_num++
                }
            }
        },
        display_loading () {
            let _this = this
            _this.pageCurrentData = []
            _this.pageData = []
            _this.total_api_num = 0
            _this.pageNum = 0
            _this.APIName = []
            _this.moreButton = false
            _this.current_api_num = 0
            let query = _this.query.trim()
            _this.$refs.result.style.display = 'none'
            if (query == '') {
                alert("The input should not be empty!")
            } else {
                _this.isActive = false
                axios
                .post(
                    _this.postUrl,
                    {'query': query})
                .then(response => {
                    console.log(response.data)
                    _this.all_code_description = response.data[0]
                    _this.total_api_num = _this.all_code_description.length
                    _this.change_data(1)
                    _this.hidden_loading()
                    _this.get_graph_id()
                    // _this.dealt_data(response.data)
                })
                .catch(error => {
                    console.log(error)
                    alert("Sorry! Network Error!")
                })
            }
        },
        get_graph_id (){
            let _this = this
            for (let i in this.all_code_description){
                let api_name = this.all_code_description[i]["name"]
                if (_this.api2graph[api_name] == null || _this.api2graph[api_name] == undefined) {
                    axios
                        .post(
                            'http://bigcode.fudan.edu.cn/kg/api/graph/searchWithBM25/',
                            {'query': api_name, "max_num": 1})
                        .then(response => {
                            let grapg_id = response.data["nodes"][0]["id"]
                            _this.api2graph[api_name] = grapg_id
                        })
                        .catch(error => {
                            console.log(error)
                        })
                }
            }
        },
        showGraph(name){
            // alert(this.api2graph[name])
            window.open("http://bigcode.fudan.edu.cn/kg/index.html#/KnowledgeData/" + this.api2graph[name]); 
        },
        every_page_first_play() {
            let data = this.all_code_description[this.APIName[this.pageNum]]
            for (let i in data){
                if (i >= 3) {
                    break
                } else {
                    this.pageCurrentData.push(data[i])
                }
            }
            console.log(this.pageCurrentData)
            this.hidden_loading()
        },
        dealt_data(data) {
            for(let i in data) {
                this.APIName.push(i)
            }
            // console.log(this.APIName)
            this.every_page_first_play()
        },
        hidden_loading () {
            this.$refs.result.style.display = ''
            this.isActive = true
        },
        example () {
            this.$refs.result.style.display = 'none'
            this.query = this.example1
        },
    }
  })