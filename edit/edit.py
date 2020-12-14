from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_login import login_required
from models import (get_all_colors, get_all_user_notes, get_color_by_id,
                    get_note_by_id, remove_note, save_note)


edit_blueprint = Blueprint('edit', __name__,
                           template_folder='templates',
                           url_prefix='/edit')


@edit_blueprint.route('/<int:note_id>', methods=['POST', 'GET'])
@login_required
def edit(note_id):
    notes_id = [note.id for note in get_all_user_notes(current_user.id)]
    if note_id not in notes_id:
        flash('This is not your note!', category='error')
        return redirect(url_for('home'))

    note = get_note_by_id(note_id)
    if request.method == 'POST':
        # if note was saved or deleted
        form = request.form
        if form.get('submit') == 'save':
            save_note(note_id, form.get('text'))
            note = get_note_by_id(note_id)
        else:
            remove_note(note_id)
            return redirect(url_for('home'))

    return render_template(
        'edit.j2',
        note=note,
        colors=get_all_colors(),
        color_by_id=get_color_by_id
    )
