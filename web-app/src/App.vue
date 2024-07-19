<template>
  <div class="main">
    <div class="mySite">
      <div 
        class="firstPage"
        v-if="page1"
      >
        <div class="description">
          Вам представлены предметы, по которым доступна 
          автоматическая проверка выполнения лабораторных работ на GitHub.
        </div>
        <div
          class="section"
          v-for="cours in courses" 
          v-bind:key="cours.id"
          v-on:click="sel=cours"
          v-bind:class="{
            'selected-border': sel == cours
          }"
        >
          {{cours.name}}
          {{cours.semester}}
          sem
          <button v-on:click="showGroups(cours.id, cours.name, cours.semester)">
            Посмотреть группы
          </button>
        </div>
      </div>

      <div
        class="secondPage"
        v-if="page2"
      >
        <button v-on:click="backToPage1()">
          Назад
        </button>
        <div class="description">
          Выбранный курс: {{curCourseName}} {{curCourseSemester}} sem
        </div>
        <div
          class="section"
          v-for="(group, idx) in groups" 
          v-bind:key="idx"
          v-on:click="sel=group"
          v-bind:class="{
            'selected-border': sel == group
          }"
        >
          Группа
          {{group}}
          <button v-on:click="showLabs(group)">
            Посмотреть лабораторные
          </button>
        </div>
      </div>
      
      
      <div
        class="registerPage"
        v-if="authorizationPage"
      >
        <div class="form">

          <div class="rightAndLeft">
              <label for="surname">Фамилия:</label>
              <input class="w-60" type="text" id="surname" name="surname" required>
          </div>
          <div class="rightAndLeft">
              <label for="name">Имя:</label>
              <input class="w-60" type="text" id="name" name="name" required>
          </div>
          <div class="rightAndLeft">
              <label for="patronymic">Отчество:</label>
              <input class="w-60" type="text" id="patronymic" name="patronymic" required>
          </div>
          <div class="rightAndLeft">
              <label for="github">Ник на github:</label>
              <input class="w-60" type="text" id="github" name="github" required>
          </div>

          <button 
            v-on:click="register(name, surname, patronymic, github)"
            class="buttonOnForm"
          >
            Подвердить
          </button>

          <button 
            v-on:click="backToPage3()"
            class="buttonOnForm"
          >
            Назад
          </button>
        </div>

      </div>


      <div
        class="thirdPage"
        v-if="page3"
      >
        <button v-on:click="backToPage2()">
          Назад
        </button>
        <div class="description">
          Выбранный курс: {{curCourseName}} {{curCourseSemester}} sem
          <br>
          Выбранная группа: {{curGroup}}
        </div>
        <div
          class="section"
          v-for="(lab, indx) in labs" 
          v-bind:key="indx"
          v-on:click="sel=lab"
          v-bind:class="{
            'selected-border': sel == lab
          }"
        >
          {{lab}}
          <button v-on:click="showAuthorizationForm()">
            Запустить проверку
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data(){
    return{
      courses: [],
      groups: [],
      labs: [],

      sel: null,
      page1: true,
      page2: false,
      page3: false,
      authorizationPage: false,

      curCourseName: "default",
      curCourseID: "default",
      curCourseSemester: "default",
      curGroup: "default",
      curLab: "default",

      name: "Имя студента",
      surname: "Фамилия студента",
      patronymic: "Отчество студента",
      github: "Name on GitHub",

    };
  },
  created(){
    this.fetchCourses();
  },
  methods:{
    async fetchCourses(){
      //заменить url на url запроса с сервера бека: serverName/courses
      const response = await fetch("./courses.json");
      const data = await response.json();
      this.courses = data;
    },

    async showGroups(courseID, courseName, courseSemester){
      //заменить url на url запроса с сервера бека: serverName/courses/${courseID}/groups 
      const response = await fetch("./groups.json");
      const data = await response.json();
      this.groups = data;
      this.curCourseID = courseID;
      this.curCourseName = courseName;
      this.curCourseSemester = courseSemester;

      this.page1 = false;
      this.page2 = true;
    },

    async showLabs(group){
      //заменить url на url запроса с сервера бека: serverName/courses/${this.curCourseID}/groups/${group}/labs 
      const response = await fetch("./labs.json");
      const data = await response.json();
      this.labs = data;
      this.curGroup = group;

      this.page2 = false;
      this.page3 = true;
    },

    async showAuthorizationForm(){
      this.authorizationPage = true;
    },

    async register(name, surname, patronymic, github){
      this.name = name;
      this.surname = surname;
      this.patronymic = patronymic;
      this.github = github;
      //отправляем регистрационный запрос на сервер
      /*let registerObject = {
        "name": this.name,
        "surname": this.surname,
        "patronymic": this.patronymic,
        "github": this.github
      };
      //заменить url на url запроса с сервера бека: /courses/${this.curCourseID}/groups/${this.curGroup}/register
      const response = await fetch("serverName/courses/${this.curCourseID}/groups/${this.curGroup}/register", {
        method: 'POST',
        headers: { 'content-type' : 'application/json'},
        body: JSON.stringify(registerObject)
        }
      );*/

      //заменить url на url запроса с сервера бека: /courses/${this.curCourseID}/groups/${this.curGroup}/register

      const response = await fetch("./afterRegister.json");
      const data = await response.json();
      alert(data.message);

      if (response.status === 422 || response.status === 200){
        this.runTheCheck(this.lab)
      }
      this.authorizationPage = false;
    },

    async runTheCheck(lab){
      this.curLab = lab;
      //запускаем проверку ЛР
      /*let githubObject = {
        "github": this.github
      };
      const response = await fetch("serverName/courses/${this.curCourseID}/groups/${this.curGroup}/labs/${this.curLab}/grade", {
        method: 'POST',
        headers: { 'content-type' : 'application/json'},
        body: JSON.stringify(githubObject)
        }
      );*/

      //заменить url на url запроса с сервера бека: /courses/${this.curCourseID}/groups/${this.curGroup}/labs/${this.curLab}/grade

      const response = await fetch("./afterCheckingWork.json");
      const data = await response.json();

      alert(data.message);
    },

    async backToPage1(){
      this.curCourseID = "default";
      this.page2 = false;
      this.page1 = true;
    },

    async backToPage2(){
      this.curGroup = "default";
      this.page3 = false;
      this.page2 = true;
    },

    async backToPage3(){
      this.curLab = "default";
      this.authorizationPage = false;
      this.page3 = true;
    }
  }
};
</script>

<style src="./styles.css">

</style>


 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
  <!--<input
    v-model="ticker"
    v-on:keydown.enter="add"
    type="text"
    name="wallet"
    id="wallet"
  />

  <label>
    Тикер {{ ticker }}
  </label>

  <button
    v-on:click="add"
    type="button"
  >
    Нажать
  </button>
  {{sel}}*/


  /*add(){
      const newTicker = {
        name: this.ticker,
        price: "-"
      }
      this.tickers.push(newTicker);
      this.ticker = "";
    },

    handleDelete(tickerToRemove){
      this.tickers=this.tickers.filter(t => t != tickerToRemove);
    }*/
  -->


    