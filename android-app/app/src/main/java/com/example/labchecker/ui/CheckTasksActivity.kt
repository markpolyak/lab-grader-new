package com.example.labchecker.ui

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat.Type.systemBars
import androidx.drawerlayout.widget.DrawerLayout
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.labchecker.R
import com.example.labchecker.data.api.CoursesService
import com.example.labchecker.data.api.GithubRequest
import com.example.labchecker.data.api.RegisterRequest
import com.example.labchecker.databinding.CheckTasksActivityBinding
import com.example.labchecker.util.adapters.LabsRecyclerViewAdapter
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.navigation.NavigationView
import dagger.hilt.android.AndroidEntryPoint
import jakarta.inject.Inject
import kotlinx.coroutines.launch

@AndroidEntryPoint
class CheckTasksActivity : AppCompatActivity() {
    private lateinit var binding: CheckTasksActivityBinding
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var topAppBar: MaterialToolbar

    @Inject
    lateinit var coursesService: CoursesService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        binding = CheckTasksActivityBinding.inflate(layoutInflater)
        setContentView(binding.root)
        // Применение отступов для основного элемента
        ViewCompat.setOnApplyWindowInsetsListener(binding.main) { v, insets ->
            val systemBars = insets.getInsets(systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        val subject = intent.getStringExtra("subject")
        val group = intent.getStringExtra("group")

        with(binding) {
            cardSubjectName.text = subject
            cardGroupName.text = group
        }
        // Инициализация DrawerLayout и Toolbar через ViewBinding
        val drawerLayout: DrawerLayout = binding.drawerLayout
        val topAppBar = binding.topAppBar

        // Настроить обработчик кликов на иконку навигации
        topAppBar.setNavigationOnClickListener {
            drawerLayout.open()
        }

        // Обработка пунктов меню в NavigationView
        val navigationView: NavigationView = binding.navView
        navigationView.setNavigationItemSelectedListener { menuItem ->
            when (menuItem.itemId) {
                R.id.btn_menu_main -> {
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
        initUI()
    }

    private fun initUI() {
        val subject = intent.getStringExtra("subject")
        val group = intent.getStringExtra("group")
        val subjectId = intent.getStringExtra("subjectId")

        lifecycleScope.launch {
            try {
                // Получение списка лабораторных работ
                val labs = subjectId?.let { coursesService.getLabs(it, group!!) }

                // Установка LayoutManager и адаптера для RecyclerView
                binding.rvLabsCheck.layoutManager = LinearLayoutManager(this@CheckTasksActivity)
                if (labs != null) {
                    binding.rvLabsCheck.adapter = LabsRecyclerViewAdapter(labs.data) { lab ->
                        // Обработка нажатия на кнопку grade в адаптере
                        gradeLab(subjectId, group!!, lab)
                    }
                }
            } catch (e: Exception) {
                Toast.makeText(this@CheckTasksActivity, "${e.message}", Toast.LENGTH_SHORT).show()
                println(e.message)
            }
        }
    }

    private fun gradeLab(subjectId: String, group: String, lab: String) {
        lifecycleScope.launch {
            try {
                val registerResponse = coursesService.register(
                    courseId = subjectId,
                    groupId = group,
                    request = loadUserData()
                )
                if (registerResponse.code() == 200 || registerResponse.code() == 422) {
                    val response = coursesService.grade(
                        courseId = subjectId,
                        groupId = group,
                        labId = lab,
                        request = GithubRequest(github = loadUserData().github)
                    )
                    if (response.isSuccessful) {
                        Toast.makeText(this@CheckTasksActivity, response.body()?.message ?: "grade submit", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    val intent = Intent(this@CheckTasksActivity, RegistrationActivity::class.java)
                    startActivity(intent)
                }
            } catch (e: Exception) {
                Toast.makeText(this@CheckTasksActivity, "Failed to submit grade: ${e.message}", Toast.LENGTH_SHORT).show()
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