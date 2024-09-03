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
import com.example.labchecker.R
import com.example.labchecker.databinding.SignInActivitiyBinding
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.navigation.NavigationView
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class RegistrationActivity : AppCompatActivity() {
    private lateinit var binding: SignInActivitiyBinding
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var topAppBar: MaterialToolbar


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        binding = SignInActivitiyBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Применение отступов для основного элемента
        ViewCompat.setOnApplyWindowInsetsListener(binding.main) { v, insets ->
            val systemBars = insets.getInsets(systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
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

        // Пример сохранения данных в кэш
        binding.btnReg.setOnClickListener {
            if (validateInputs()) {
                val name = binding.tfName.text.toString()
                val surname = binding.tfSurname.text.toString()
                val patronymic = binding.tfPatronymic.text.toString()
                val github = binding.tfGithubNickname.text.toString()

                // Сохранение данных в SharedPreferences
                saveUserData(name, surname, patronymic, github)

                Toast.makeText(this, "Данные сохранены", Toast.LENGTH_SHORT).show()
                val intent = Intent(this, MainActivity::class.java)
                startActivity(intent)
            } else {
                Toast.makeText(this, "Пожалуйста, заполните все поля", Toast.LENGTH_SHORT).show()
            }
        }
    }


    // Проверка заполнения всех полей
    private fun validateInputs(): Boolean {
        val name = binding.tfName.text.toString().trim()
        val surname = binding.tfSurname.text.toString().trim()
        val patronymic = binding.tfPatronymic.text.toString().trim()
        val github = binding.tfGithubNickname.text.toString().trim()

        return name.isNotEmpty() && surname.isNotEmpty() && patronymic.isNotEmpty() && github.isNotEmpty()
    }

    override fun onBackPressed() {
        if (validateInputs()) {
            super.onBackPressed() // Позволяет пользователю покинуть активность
        } else {
            Toast.makeText(this, "Пожалуйста, заполните все поля", Toast.LENGTH_SHORT).show()
        }
    }
    // Сохранение данных в SharedPreferences
    private fun saveUserData(name: String, surname: String, patronymic: String, github: String) {
        val sharedPreferences = getSharedPreferences("user_data", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            putString("name", name)
            putString("surname", surname)
            putString("patronymic", patronymic)
            putString("github", github)
            apply() // Используем apply(), чтобы изменения были сохранены асинхронно
        }
    }
}
