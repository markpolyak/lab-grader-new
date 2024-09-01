import disnake
from disnake import MessageInteraction
from disnake.ext import commands

from .cogs_utils.check_lab.check_lab_utils import SelectTemplate, create_lr_embed, StudentDataModal, get_courses_info, \
    get_groups_list, get_labs_list


class SelectLab(SelectTemplate):
    def __init__(self, custom_id, items_list, placeholder, ctx, view, users_info):
        super().__init__(custom_id=custom_id,
                         items_list=items_list,
                         placeholder=placeholder,
                         ctx=ctx,
                         view=view)
        self.users_info = users_info

    async def callback(self, interaction: MessageInteraction):
        await super().callback(interaction)
        self.users_info['lab'] = self.chosen_value
        await interaction.response.send_modal(StudentDataModal(self.ctx, self.users_info))


class SelectGroup(SelectTemplate):
    def __init__(self, custom_id, items_list, placeholder, ctx, view, users_info):
        super().__init__(custom_id=custom_id,
                         items_list=items_list,
                         placeholder=placeholder,
                         ctx=ctx,
                         view=view)
        self.users_info = users_info

    async def callback(self, interaction: MessageInteraction):
        await super().callback(interaction)

        self.users_info['group'] = self.chosen_value

        labs = get_labs_list(self.users_info['course'], self.users_info['group'])

        group_select_form = SelectLab('lab_select_form',
                                      labs,
                                      'Выберите лабораторную работу',
                                      self.ctx,
                                      self.bot_view,
                                      self.users_info)
        self.bot_view.add_item(group_select_form)

        embed = create_lr_embed("Выберите лабораторную работу")
        await self.ctx.send(embed=embed, view=self.bot_view)


class ChainSelectLabParameters(SelectTemplate):
    def __init__(self, custom_id, courses_info, placeholder, ctx, view, bot):
        super().__init__(custom_id=custom_id,
                         items_list=list(courses_info.keys()),
                         placeholder=placeholder,
                         ctx=ctx,
                         view=view)
        self.bot_obj = bot
        self.courses_info = courses_info

    async def callback(self, interaction: MessageInteraction):
        await super().callback(interaction)

        course_id = self.courses_info[self.chosen_value]
        users_info = {
            'course': course_id
        }
        groups = get_groups_list(users_info["course"])

        group_select_form = SelectGroup('group_select_form', groups, 'Выберите группу', self.ctx, self.bot_view, users_info)
        self.bot_view.add_item(group_select_form)

        embed = create_lr_embed("Выберите группу")
        await self.ctx.send(embed=embed, view=self.bot_view)


class CheckLab(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def check(self, ctx):
        view = disnake.ui.View()

        courses_dict = get_courses_info()

        subject_select_form = ChainSelectLabParameters('subjects_select_form',
                                                       courses_dict,
                                                       'Выберите предмет',
                                                       ctx,
                                                       view,
                                                       self.bot)
        view.add_item(subject_select_form)

        embed = create_lr_embed("Выберите предмет")
        await ctx.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(CheckLab(bot))
