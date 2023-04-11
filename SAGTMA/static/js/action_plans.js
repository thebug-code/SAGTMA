$(document).ready(function() {
  // Agregar un nuevo plan de acción
  $(document).on('click', '.add-action-plan', function() {
    var form = $(this);
    id = form.attr("id").match(/\d+/)[0];

    $.getJSON({
      url: "/api/v1/action-plans-dropdown-data",
      success: function(data) {
        $("#add-action-plan-modal").modal("show");
        var users = data.users;
        var actions = data.actions;
        var units = data.measureUnits;

        // Obtener el select de usuarios y vaciar su contenido
        const addPlanChargePersonSelect = $("#add-charge-person");
        addPlanChargePersonSelect.empty();

        // Agregar una opción por cada usuario
        users.forEach(function(user) {
          const option = $("<option>").attr("value", user.id).text(user.names + " " + user.surnames);

          // Agregar la opción al select
          addPlanChargePersonSelect.append(option);
        });

        // Obtener los campos de acción existente y nueva acción
        const existingActionFields = $("#existing-action-fields");
        const newActionFields = $("#new-action-fields");

        // Obtener los select de accion existente
        const existingActionSelect = $("#existing-action");

        // Obtener el campo de nueva acción
        const newActionInput = $("#new-action");

        // Obtener el select de tipo de acción
        const actionTypeSelect = $("#action-type");

        // Agregar un listener para detectar cambios
        actionTypeSelect.change(function() {
          // Obtener el valor del select
          const actionType = $(this).val();

          // Actualizar el campo oculto "action-type-hidden" cada vez que cambie el valor del campo
          // "Tipo de acción"
          $("#action-type-hidden").val(actionType);

          // Mostrar u ocultar los campos según la opción seleccionada
          if (actionType === "existing") {
            newActionInput.prop("required", false);
            existingActionSelect.prop("required", true);
            newActionFields.hide();
            existingActionFields.show();
            
            // Obtener el select de acciones y vaciar su contenido
            const actionsSelect = existingActionFields.children().eq(1);
            actionsSelect.empty();

            // Agregar opción "Seleccione una opción"
            const defaultOption = $("<option>")
              .attr("value", "")
              .attr("disabled", true)
              .attr("selected", true)
              .text("Seleccione una acción");
            actionsSelect.append(defaultOption);

            // Agregar una opción por cada acción
            actions.forEach(function(action) {
              const option = $("<option>").attr("value", action.id).text(action.description);

              // Agregar la opción al select
              actionsSelect.append(option);
            });
          } else if (actionType === "new") {
            existingActionSelect.prop("required", false);
            newActionInput.prop("required", true);
            existingActionFields.hide();
            newActionFields.show();
          } else {
            existingActionSelect.prop("required", false);
            newActionInput.prop("required", false);
            existingActionFields.hide();
            newActionFields.hide();
          }
        });

        // Obtener el select de unidades de medida y vaciar su contenido
        const measureUnitSelect = $("#measure-unit-ms");
        measureUnitSelect.empty();

        // Agregar opción "Seleccione una opción"
        const defaultOption = $("<option>")
          .attr("value", "")
          .attr("disabled", true)
          .attr("selected", true)
          .text("Seleccione una unidad de medida");
        measureUnitSelect.append(defaultOption);

        // Agregar una opción por cada unidad de medida
        units.forEach(function(unit) {
          const option = $("<option>").attr("value", unit.id).text(unit.dimension).text(unit.unit);
          
          // Agregar la opción al select
          measureUnitSelect.append(option);
        });

        $("#add-action-plan-form").attr("action", "/action-plans/" + id + "/register/");
      },
    });
  });

  // Eliminar un plan de acción
  $(document).on('click', '.delete-action-plan', function() {
    var form = $(this);
    id = form.attr("id").match(/\d+/)[0];

    $("#delete-action-plan-modal").modal("show");
    $("#delete-action-plan-form").attr("action", "/action-plans/" + id + "/delete/");
  });

  // Editar un plan de acción
  $(document).on('click', '.edit-action-plan', function(event) {
    const actionId = $(event.currentTarget).attr('data-action-id');
    const activityId = $(event.currentTarget).attr('data-activity-id');

    $.getJSON({
      url: "/api/v1/action-plans",
      data: { action_id: actionId, activity_id: activityId },
      success: function(data) {
        $("#edit-action-plan-modal").modal("show");
        const actionPlan = data.actionPlans[actionId];
        const activity = actionPlan.activities[0];
        const users = data.users;

        // Obtener el select de usuarios y vaciar su contenido
        const editPlanChargePersonSelect = $("#edit-charge-person");
        editPlanChargePersonSelect.empty();

        // Agregar una opción por cada usuario
        users.forEach(function(user) {
          const option = $("<option>").attr("value", user.id).text(user.names + " " + user.surnames);
          
          // Si el usuario es el responsable del plan de acción, seleccionarlo
          // por defecto
          if (user.id === actionPlan.charge_person_id) {
            option.attr("selected", "selected");
          }

          // Agregar la opción al select
          editPlanChargePersonSelect.append(option);
        });

        $("#edit-action").val(actionPlan.action);
        $("#edit-activity").val(activity.description);
        $("#edit-start-date").val(activity.start_date);
        $("#edit-deadline").val(activity.deadline);
        $("#edit-work-hours").val(activity.work_hours);
        $("#edit-cost").val(activity.cost);

        // Establecer los valores de los inputs
        $('#activity-id').val(activityId);
        $('#action-id').val(actionId);

        $("#edit-action-plan-form").attr("action", "/action-plans/" + actionId + "/edit/");
      },
    });
  });
});

      
