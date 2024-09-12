package com.example.labchecker.ui

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat.Type.systemBars
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.lifecycleScope
import com.example.labchecker.R
import com.example.labchecker.data.api.CoursesService
import com.example.labchecker.data.api.GithubRequest
import com.example.labchecker.data.api.RegisterRequest
import com.example.labchecker.databinding.ActivityMainBinding
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.navigation.NavigationView
import kotlinx.coroutines.launch
import javax.inject.Inject
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var topAppBar: MaterialToolbar

    @Inject
    lateinit var coursesService: CoursesService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Применение отступов для основного элемента
        ViewCompat.setOnApplyWindowInsetsListener(binding.main) { v, insets ->
            val systemBars = insets.getInsets(systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        if (loadUserData().name == "") {
            val intent = Intent(this, RegistrationActivity::class.java)
            startActivity(intent)
        } else {
            println(loadUserData())
        }


        // Инициализация DrawerLayout и Toolbar через ViewBinding
        drawerLayout = binding.drawerLayout
        topAppBar = binding.topAppBar

        // Настроить обработчик кликов на иконку навигации
        topAppBar.setNavigationOnClickListener {
            drawerLayout.open()
        }

        // Обработка пунктов меню в NavigationView
        val navigationView: NavigationView = binding.navView
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.btn_menu_main -> {
                    // Можно обновить текущую активность или просто использовать этот вызов для навигации
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                }
                R.id.btn_menu_reg -> {
                    val intent = Intent(this, RegistrationActivity::class.java)
                    startActivity(intent)
                }
            }

            // Закрыть меню после выбора элемента
            drawerLayout.close()
            true
        }

        // Инициализация UI и загрузка данных
        initUI()
    }

    private fun initUI() {
        lifecycleScope.launch {
            try {
                // Получение списка предметов
                val subjects = coursesService.getSubjects()

                // Создание списка имен предметов
                val subjectNames = subjects.map { it.name }
                val subjectMap = subjects.associateBy { it.name }

                // Инициализация адаптера для предметов
                val subjectsTextView: AutoCompleteTextView = binding.menuSubjects
                val adapterSubject = ArrayAdapter(this@MainActivity, android.R.layout.simple_dropdown_item_1line, subjectNames)
                subjectsTextView.setAdapter(adapterSubject)

                // Настройка обработчика кликов для выбора предмета
                val groupsTextView: AutoCompleteTextView = binding.menuGroup
                subjectsTextView.setOnItemClickListener { parent, _, position, _ ->
                    val selectedSubjectName = parent.getItemAtPosition(position).toString()
                    val selectedSubject = subjectMap[selectedSubjectName]

                    if (selectedSubject != null) {
                        lifecycleScope.launch {
                            try {
                                // Получение групп для выбранного предмета
                                val groups = coursesService.getGroups(selectedSubject.id)
                                // Инициализация адаптера для групп
                                val adapterGroup = ArrayAdapter(this@MainActivity, android.R.layout.simple_dropdown_item_1line, groups.data)
                                groupsTextView.setAdapter(adapterGroup)
                            } catch (e: Exception) {
                                // Обработка ошибок, если запрос не удался
                                Toast.makeText(this@MainActivity, "Ошибка получения групп: ${e.message}", Toast.LENGTH_SHORT).show()
                                println(e.message)
                            }
                        }
                    }
                }

                // Обработка нажатия кнопки "Найти задачи"
                binding.btnFindTasks.setOnClickListener {
                    val selectedSubjectName = subjectsTextView.text.toString()
                    val selectedGroup = groupsTextView.text.toString()
                    val selectedSubject = subjectMap[selectedSubjectName]

                    if (selectedSubject == null) {
                        Toast.makeText(this@MainActivity, "Пожалуйста, выберите предмет", Toast.LENGTH_SHORT).show()
                    } else if (selectedGroup.isEmpty()) {
                        Toast.makeText(this@MainActivity, "Пожалуйста, выберите группу", Toast.LENGTH_SHORT).show()
                    } else {
                        // Переход к CheckTasksActivity с передачей выбранных значений
                        val intent = Intent(this@MainActivity, CheckTasksActivity::class.java)
                        intent.putExtra("subject", selectedSubjectName)
                        intent.putExtra("group", selectedGroup)
                        intent.putExtra("subjectId", selectedSubject.id)
                        startActivity(intent)
                    }
                }

            } catch (e: Exception) {
                // Обработка ошибок, если запрос не удался
                Toast.makeText(this@MainActivity, "Ошибка загрузки данных: ${e.message}", Toast.LENGTH_SHORT).show()
                println(e.message)
            }
        }
    }
    // Загрузка данных из SharedPreferences
    private fun loadUserData() : RegisterRequest {
        val sharedPreferences = getSharedPreferences("user_data", Context.MODE_PRIVATE)

        // Получаем данные из SharedPreferences
        val name = sharedPreferences.getString("name", "")
        val surname = sharedPreferences.getString("surname", "")
        val patronymic = sharedPreferences.getString("patronymic", "")
        val github = sharedPreferences.getString("github", "")
        return RegisterRequest(name!!,surname!!,patronymic!!,github!!)
    }
}
